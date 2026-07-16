import sys
import re
from pathlib import Path

IMMEDIATE_REGEX = re.compile(r'#(\w+)')
ADDRESS_REGEX = re.compile(r'^(0x[0-9a-fA-F]+|\d+)$')
LABEL_REGEX = re.compile(r'^([a-zA-Z_][a-zA-Z0-9_]*):$')

OPCODES_1BYTE = {
    "NOP":  0x00,
    "ADD B": 0x04,
    "ADC B": 0x05,
    "SUB B": 0x06,
    "AND B": 0x07,
    "OR B":  0x08,
    "XOR B": 0x09,
    "NOTA":  0x0A,
    "TAX":   0x0E,
    "TXA":   0x0F,
    "TAB":   0x10,
    "TBA":   0x11,
    "INCA":  0x12,
    "DECA":  0x13,
    "PUSH":  0x14,
    "POP":   0x15,
    "RET":   0x17,
    "HLT":   0xFF
}
OPCODES_3BYTE = {
    "LDA": 0x02,
    "STA": 0x03,
    "JMP": 0x0B,
    "JZ":  0x0C,
    "JC":  0x0D,
    "CALL": 0x16
}

def parse_number(val_str):
    if val_str.lower().startswith('0x'):
        return int(val_str, 16)
    return int(val_str, 10)

def assemble_line(line, line_num, symbol_table):
    # tokenize the line into mnemonic and arguments
    parts = line.split(maxsplit=1)
    mnemonic = parts[0].upper()
    args = parts[1].strip() if len(parts) > 1 else ""

    # handle DB
    if mnemonic == "DB":
        if not args:
            raise SyntaxError(f"Line {line_num}: DB directive requires a value.")
        val = parse_number(args)
        if not (0 <= val <= 255):
            raise ValueError(f"Line {line_num}: DB value {val} out of 8-Bit Range!")
        return bytes([val])

    # reconstruct full instruction for easier matching
    full_instruction = f"{mnemonic} {args}".strip().upper()

    # 1-BYTE INSTRUCTIONS
    if full_instruction in OPCODES_1BYTE:
        return bytes([OPCODES_1BYTE[full_instruction]])

    # 2-BYTE INSTRUCTIONS
    if mnemonic == "LDA" and args.startswith("#"):
        match = IMMEDIATE_REGEX.match(args)
        if match:
            val = parse_number(match.group(1))
            if not (0 <= val <= 255):
                raise ValueError(f"Line {line_num}: Immediate Value {val} out of 8-Bit Range!")
            return bytes([0x01, val])

    # 3-BYTE INSTRUCTIONS
    if mnemonic in OPCODES_3BYTE:
        if args in symbol_table:
            addr = symbol_table[args]
        else:
            match = ADDRESS_REGEX.match(args)
            if match:
                addr = parse_number(match.group(1))
            else:
                raise SyntaxError(f"Line {line_num}: Invalid address or undefined label: '{args}'")
                
        if not (0 <= addr <= 65535):
            raise ValueError(f"Line {line_num}: Address {hex(addr)} out of 16-Bit Range!")

        opcode = OPCODES_3BYTE[mnemonic]
        adrl = addr & 0xFF
        adrh = (addr >> 8) & 0xFF
        return bytes([opcode, adrl, adrh])

    raise SyntaxError(f"Line {line_num}: Unknown instruction or incorrect format: '{line}'")


def assemble(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        rawlines = f.readlines()
    
    symbol_table = {}
    pc = 0
    cleaned_code = []
    
    # First pass: calculate addresses and find labels
    for line_num, line in enumerate(rawlines, start=1):
        # remove comments and whitespace
        line = line.split(';')[0].strip()
        if not line:
            # ignore empty lines
            continue

        # Handle ORG
        if line.upper().startswith("ORG"):
            parts = line.split(maxsplit=1)
            pc = parse_number(parts[1])
            continue

        # handle EQU
        tokens = line.split()
        if len(tokens) >= 3 and tokens[1].upper() == 'EQU':
            label = tokens[0]
            if label in symbol_table:
                raise ValueError(f"Line {line_num}: Duplicate label/constant '{label}' found.")
            symbol_table[label] = parse_number(tokens[2])
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
        full_inst = f"{mnemonic} {args}".strip().upper()

        if full_inst in OPCODES_1BYTE:
            pc += 1
        elif mnemonic == "LDA" and args.startswith("#"):
            pc += 2
        elif mnemonic in OPCODES_3BYTE:
            pc += 3
        else:
            raise SyntaxError(f"Line {line_num}: Unknown instruction: '{line}'")

    # Second pass: generate machine code
    binary_data = bytearray()

    for line_num, line in cleaned_code:
        try:
            machine_code = assemble_line(line, line_num, symbol_table)
            if machine_code:
                binary_data.extend(machine_code)
        except Exception as e:
            print(f"Error while assembling: {e}")
            sys.exit(1)
                
    with open(output_file, 'wb') as f:
        f.write(binary_data)
    
    print(f"Successfully assembled! {len(binary_data)} bytes written to '{output_file}'.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python assembler.py <input.asm> <output.bin>")
        sys.exit(1)
        
    input_path = Path(sys.argv[1])
    
    if len(sys.argv) >= 3:
        output_path = Path(sys.argv[2])
    else:
        output_path = input_path.with_suffix('.bin')
        
    assemble(str(input_path), str(output_path))