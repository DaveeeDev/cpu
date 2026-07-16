import sys
from pathlib import Path
from sly import Lexer, Parser

_ = None

class CFlatLexer(Lexer):
    tokens = { "ID", "NUMBER", "ASSIGN", "PLUS", "SEMI", "INT" }
    
    ignore = ' \t\r\n'

    ASSIGN = r'='
    PLUS   = r'\+'
    SEMI   = r';'

    ID = r'[a-zA-Z_][a-zA-Z0-9_]*'
    ID['int'] = "INT"

    @_(r'\d+')
    def NUMBER(self, t):
        t.value = int(t.value)
        return t

class CFlatParser(Parser):
    tokens = CFlatLexer.tokens

    def __init__(self):
        self.variables = {}
        self.next_var_address = 0x0000

    @_('statements statement')
    def statements(self, p):
        return p.statements + [p.statement]

    @_('statement')
    def statements(self, p):
        return [p.statement]

    @_('INT ID SEMI')
    def statement(self, p):
        var_name = p.ID
        if var_name not in self.variables:
            self.variables[var_name] = self.next_var_address
            self.next_var_address += 1
            
            if self.next_var_address > 0x00FF:
                raise MemoryError("Zero Page RAM overflow! Too many variables.")
        return ""

    @_('ID ASSIGN NUMBER SEMI')
    def statement(self, p):
        return f"    LDA #0x{p.NUMBER:02X}\n    STA {p.ID}"

    @_('ID ASSIGN ID PLUS ID SEMI')
    def statement(self, p):
        target = p.ID0
        var1 = p.ID1
        var2 = p.ID2
        return f"    LDA {var1}\n    TAB\n    LDA {var2}\n    ADD B\n    STA {target}"

# --- 3. THE COMPILER DRIVER ---
def compile_file(input_file, output_file):
    with open(input_file, 'r') as f:
        code = f.read()

    lexer = CFlatLexer()
    parser = CFlatParser()

    # Generate lines of assembly
    parsed_lines = parser.parse(lexer.tokenize(code))
    
    # Filter out empty lines (like from variable declarations)
    assembly_lines = [line for line in parsed_lines if line.strip()]

    # Generate EQU directives for each allocated variable
    equ_declarations = []
    for var_name, addr in parser.variables.items():
        equ_declarations.append(f"{var_name} EQU 0x{addr:04X}")

    # Build the final assembly structure
    final_assembly = "    ORG 0x0200\n\n"
    final_assembly = "; --- Variable Allocations ---\n"
    final_assembly += "\n".join(equ_declarations) + "\n\n"
    final_assembly += "; --- Program Code ---\n"
    final_assembly += "    ORG 0x0200\n\n"
    final_assembly += "\n".join(assembly_lines)
    final_assembly += "\n\n    HLT\n"

    with open(output_file, 'w') as f:
        f.write(final_assembly)
        
    print(f"Successfully compiled {input_file} -> {output_file}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python compiler.py <input.cflat>")
        sys.exit(1)
        
    input_path = Path(sys.argv[1])
    output_path = input_path.with_suffix('.asm')
    
    compile_file(str(input_path), str(output_path))