import sys
import re
from pathlib import Path

IMMEDIATE_REGEX = re.compile(r'#(\w+)')
ADDRESS_REGEX = re.compile(r'^(0x[0-9a-fA-F]+|\d+)$')

def parse_number(val_str):
    if val_str.lower().startswith('0x'):
        return int(val_str, 16)
    return int(val_str, 10)

def assemble_line(line, line_num):
    # remove comments and whitespace
    line = line.split(';')[0].strip()
    if not line:
        # ignore empty lines
        return None
    
    # tokenize the line into mnemonic and arguments
    parts = line.split(maxsplit=1)
    mnemonic = parts[0].upper()
    args = parts[1].strip() if len(parts) > 1 else ""

    # reconstruct full instruction for easier matching
    full_instruction = f"{mnemonic} {args}".strip().upper()

    opcodes_1byte = {
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
        "HLT":   0xFF
    }

    # 1-BYTE INSTRUCTIONS
    if full_instruction in opcodes_1byte:
        return bytes([opcodes_1byte[full_instruction]])

    # 2-BYTE INSTRUCTIONS
    if mnemonic == "LDA" and args.startswith("#"):
        match = IMMEDIATE_REGEX.match(args)
        if match:
            val = parse_number(match.group(1))
            if not (0 <= val <= 255):
                raise ValueError(f"Line {line_num}: Immediate Value {val} out of 8-Bit Range!")
            return bytes([0x01, val])

    # 3-BYTE INSTRUCTIONS
    opcodes_3byte = {
        "LDA": 0x02,
        "STA": 0x03,
        "JMP": 0x0B,
        "JZ":  0x0C,
        "JC":  0x0D
    }

    if mnemonic in opcodes_3byte:
        match = ADDRESS_REGEX.match(args)
        if match:
            addr = parse_number(match.group(1))
            if not (0 <= addr <= 65535):
                raise ValueError(f"Line {line_num}: Address {hex(addr)} out of 16-Bit Range!")
            
            opcode = opcodes_3byte[mnemonic]
            adrl = addr & 0xFF
            adrh = (addr >> 8) & 0xFF
            return bytes([opcode, adrl, adrh])

    raise SyntaxError(f"Line {line_num}: Unknown instruction or incorrect format: '{line}'")


def assemble(input_file, output_file):
    binary_data = bytearray()
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, start=1):
            try:
                machine_code = assemble_line(line, line_num)
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