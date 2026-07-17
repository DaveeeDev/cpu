import sys
from pathlib import Path

OPCODES_1BYTE = {
    "NOP":   0x00,
    "ADD B": 0x06,
    "ADC B": 0x07,
    "SUB B": 0x08,
    "AND B": 0x09,
    "OR B":  0x0A,
    "XOR B": 0x0B,
    "NOTA":  0x0C,
    "TAX":   0x10,
    "TXA":   0x11,
    "TAB":   0x12,
    "TBA":   0x13,
    "INCA":  0x14,
    "DECA":  0x15,
    "PUSH":  0x16,
    "POP":   0x17,
    "RET":   0x19,
    "HLT":   0xFF
}
OPCODES_2BYTE = {
    "LDAX":  0x03,
    "STAX":  0x05
}
OPCODES_3BYTE = {
    "LDA":  0x02,
    "STA":  0x04,
    "JMP":  0x0D,
    "JZ":   0x0E,
    "JC":   0x0F,
    "CALL": 0x18
}

def parse_number(val_str):
    if val_str.lower().startswith('0x'):
        return int(val_str, 16)
    return int(val_str, 10)

def get_instruction_length(mnemonic, args):
    mnemonic = mnemonic.upper()
    full_inst = f"{mnemonic} {args}".strip().upper()

    if mnemonic == "DB":
        return 1
    if full_inst in OPCODES_1BYTE:
        return 1
    if mnemonic == "LDA" and args.startswith("#"):
        return 2
    if mnemonic in OPCODES_2BYTE:
        return 2
    if mnemonic in OPCODES_3BYTE:
        return 3
    return None

def resolve_argument(arg_str, line_num, symbol_table, limit_8bit=False):
    arg_str = arg_str.strip()
    if not arg_str:
        raise SyntaxError(f"Line {line_num}: Missing expected argument.")

    # check for low '<' or high '>' byte operator
    get_low = False
    get_high = False
    if arg_str.startswith("<"):
        get_low = True
        arg_str = arg_str[1:].strip()
    elif arg_str.startswith(">"):
        get_high = True
        arg_str = arg_str[1:].strip()

    # get value
    if arg_str in symbol_table:
        val = symbol_table[arg_str]
    else:
        try:
            val = parse_number(arg_str)
        except ValueError:
            raise SyntaxError(f"Line {line_num}: Undefined label or invalid syntax: '{arg_str}'")

    # apply extraction operators if used
    if get_low:
        val = val & 0xFF
    elif get_high:
        val = (val >> 8) & 0xFF

    if limit_8bit:
        if not (0 <= val <= 255):
            raise ValueError(f"Line {line_num}: Resolved 8-bit value {hex(val)} is out of range!")
    else:
        if not (0 <= val <= 65535):
            raise ValueError(f"Line {line_num}: Resolved 16-bit address {hex(val)} is out of range!")

    return val



def assemble_line(line, line_num, symbol_table):
    # tokenize the line into mnemonic and arguments
    parts = line.split(maxsplit=1)
    mnemonic = parts[0].upper()
    args = parts[1].strip() if len(parts) > 1 else ""

    # handle DB
    if mnemonic == "DB":
        val = resolve_argument(args, line_num, symbol_table, limit_8bit=True)
        return bytes([val])

    # reconstruct full instruction for easier matching
    full_instruction = f"{mnemonic} {args}".strip().upper()

    # 1-BYTE INSTRUCTIONS
    if full_instruction in OPCODES_1BYTE:
        return bytes([OPCODES_1BYTE[full_instruction]])

    # 2-BYTE INSTRUCTIONS
    if mnemonic == "LDA" and args.startswith("#"):
        # Strip the '#' prefix and evaluate as 8-bit limit
        imm_str = args[1:].strip()
        val = resolve_argument(imm_str, line_num, symbol_table, limit_8bit=True)
        return bytes([0x01, val])

    if mnemonic in OPCODES_2BYTE:
        val = resolve_argument(args, line_num, symbol_table, limit_8bit=True)
        opcode = OPCODES_2BYTE[mnemonic]
        return bytes([opcode, val])

    # 3-BYTE INSTRUCTIONS
    if mnemonic in OPCODES_3BYTE:
        addr = resolve_argument(args, line_num, symbol_table, limit_8bit=False)
        opcode = OPCODES_3BYTE[mnemonic]
        return bytes([opcode, addr & 0xFF, (addr >> 8) & 0xFF])

    raise SyntaxError(f"Line {line_num}: Unknown instruction or incorrect format: '{line}'")


def assemble(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        rawlines = f.readlines()
    
    symbol_table = {}
    pc = 0x0200  # Default starting address
    cleaned_code = []
    
    # First pass: calculate addresses and find labels
    for line_num, line in enumerate(rawlines, start=1):
        # remove comments and whitespace
        line = line.split(';')[0].strip()
        if not line:
            # ignore empty lines
            continue

        # handle EQU
        tokens = line.split()
        if len(tokens) >= 3 and tokens[1].upper() == 'EQU':
            label = tokens[0]
            if label in symbol_table:
                raise ValueError(f"Line {line_num}: Duplicate label/constant '{label}' found.")
            
            val_str = tokens[2]
            symbol_table[label] = symbol_table[val_str] if val_str in symbol_table else parse_number(val_str)
            continue

        # Handle ORG
        if line.upper().startswith("ORG"):
            parts = line.split(maxsplit=1)
            org_val = parts[1].strip()
            if org_val in symbol_table:
                pc = symbol_table[org_val]
            else:
                try:
                    pc = parse_number(org_val)
                except ValueError:
                    raise SyntaxError(f"Line {line_num}: Invalid or undefined ORG address '{org_val}'")
            continue

        if ':' in line:
            label, line = line.split(':', 1)
            label = label.strip()
            line = line.strip()
            if label in symbol_table:
                raise ValueError(f"Line {line_num}: Duplicate label '{label}' found.")
            symbol_table[label] = pc
            if not line:
                continue

        cleaned_code.append((line_num, line))
        parts = line.split(maxsplit=1)
        mnemonic = parts[0].upper()
        args = parts[1].strip() if len(parts) > 1 else ""

        length = get_instruction_length(mnemonic, args)
        if length is None:
            raise SyntaxError(f"Line {line_num}: Unknown instruction layout: '{line}'")
        pc += length

    # Second pass: generate machine code
    binary_data = bytearray()

    for line_num, line in cleaned_code:
        try:
            machine_code = assemble_line(line, line_num, symbol_table)
            if machine_code:
                binary_data.extend(machine_code)
        except Exception as e:
            print(f"Error while assembling line {line_num}: {e}")
            sys.exit(1)
                
    with open(output_file, 'wb') as f:
        f.write(binary_data)
    
    print(f"Successfully assembled! {len(binary_data)} bytes written to '{output_file}'.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python assembler.py <input.asm> [<output.bin>]")
        sys.exit(1)
        
    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2]) if len(sys.argv) >= 3 else input_path.with_suffix('.bin')
    assemble(str(input_path), str(output_path))