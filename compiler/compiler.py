import sys
from pathlib import Path
from sly import Lexer, Parser

_ = None


class AST:
    pass

class Block(AST):
    def __init__(self, statements):
        self.statements = statements

class Number(AST):
    def __init__(self, value):
        self.value = value

class Identifier(AST):
    def __init__(self, name):
        self.name = name

class BinOp(AST):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

class Assign(AST):
    def __init__(self, target, valueNode):
        self.targetName = target
        self.valueNode = valueNode

class VarDecl(AST):
    def __init__(self, name):
        self.name = name

class ConstDecl(AST):
    def __init__(self, name, value):
        self.name = name
        self.value = value

class IfStmt(AST):
    def __init__(self, condition, true_block, false_block=None):
        self.condition = condition
        self.true_block = true_block
        self.false_block = false_block

class WhileStmt(AST):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class BreakStmt(AST):
    pass


class CFlatLexer(Lexer):
    tokens = { "ID", "NUMBER", "PLUS", "MINUS", "TIMES", "DIV", "LPAREN",
               "RPAREN", "LBRACE", "RBRACE", "EQEQ", "NEQ", "ASSIGN",
               "SEMI", "CONST", "UINT", "BOOL", "TRUE", "FALSE", "IF",
               "ELSE", "WHILE", "BREAK", "FOR" }

    ignore = ' \t\r'

    @_(r'//.*\n')
    def ignore_comment(self, t):
        self.lineno += 1

    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += t.value.count('\n')

    PLUS   = r'\+'
    MINUS  = r'\-'
    TIMES  = r'\*'
    DIV    = r'\/'
    LPAREN = r'\('
    RPAREN = r'\)'
    LBRACE = r'\{'
    RBRACE = r'\}'
    EQEQ   = r'=='
    NEQ    = r'!='
    ASSIGN = r'='
    SEMI   = r';'

    ID = r'[a-zA-Z_][a-zA-Z0-9_]*'
    ID['const'] = "CONST"
    ID['uint8'] = "UINT"
    ID['bool']  = "BOOL"
    ID['true']  = "TRUE"
    ID['false'] = "FALSE"
    ID['if']    = "IF"
    ID['else']  = "ELSE"
    ID['while'] = "WHILE"
    ID['break'] = "BREAK"
    ID['for']   = "FOR"

    @_(r'\d+')
    def NUMBER(self, t):
        t.value = int(t.value)
        return t

    def error(self, t):
        print(f"Illegal character '{t.value[0]}' on line {self.lineno}")
        self.index += 1

class CFlatParser(Parser):
    tokens = CFlatLexer.tokens

    precedence = (
        ('left', "EQEQ", "NEQ"),
        ('left', "PLUS", "MINUS"),
        ('left', "TIMES", "DIV"),
    )

    def __init__(self):
        self.variables = {}
        self.next_var_address = 0x0000

    @_('statements statement')
    def statements(self, p):
        return p.statements + [p.statement]

    @_('statement')
    def statements(self, p):
        return [p.statement]

    # unsigned integer declaration
    @_('UINT ID SEMI')
    def statement(self, p):
        return VarDecl(p.ID)

    # constant declaration
    @_('CONST UINT ID ASSIGN NUMBER SEMI')
    def statement(self, p):
        return ConstDecl(p.ID, p.NUMBER)

    # boolean declaration
    @_('BOOL ID SEMI')
    def statement(self, p):
        return VarDecl(p.ID)

    # variable assignment
    @_('ID ASSIGN expr SEMI')
    def statement(self, p):
        return Assign(p.ID, p.expr)

    # if-else statement
    @_('IF LPAREN expr RPAREN LBRACE statements RBRACE ELSE LBRACE statements RBRACE')
    def statement(self, p):
        return IfStmt(p.expr, p.statements0, p.statements1)

    # if statement
    @_('IF LPAREN expr RPAREN LBRACE statements RBRACE')
    def statement(self, p):
        return IfStmt(p.expr, p.statements, [])

    # while loop
    @_('WHILE LPAREN expr RPAREN LBRACE statements RBRACE')
    def statement(self, p):
        return WhileStmt(p.expr, p.statements)

    # break statement
    @_('BREAK SEMI')
    def statement(self, p):
        return BreakStmt()

    # desugared for loop
    @_('FOR LPAREN ID ASSIGN expr SEMI expr SEMI ID ASSIGN expr RPAREN LBRACE statements RBRACE')
    def statement(self, p):
        init_node = Assign(p.ID0, p.expr0)
        condition_node = p.expr1
        step_node = Assign(p.ID1, p.expr2)

        while_body = p.statements + [step_node]
        while_node = WhileStmt(condition_node, while_body)

        return Block([init_node, while_node])

    # arithmetic expressions
    @_('expr PLUS expr', 'expr MINUS expr', 'expr TIMES expr', 'expr DIV expr', 'expr EQEQ expr', 'expr NEQ expr')
    def expr(self, p):
        return BinOp(p[1], p.expr0, p.expr1)

    # parentheses
    @_('LPAREN expr RPAREN')
    def expr(self, p):
        return p.expr

    # number
    @_('NUMBER')
    def expr(self, p):
        return Number(p.NUMBER)

    # identifier
    @_('ID')
    def expr(self, p):
        return Identifier(p.ID)

    # boolean true
    @_('TRUE')
    def expr(self, p):
        return Number(1)

    # boolean false
    @_('FALSE')
    def expr(self, p):
        return Number(0)

class CodeGenerator:
    def __init__(self):
        self.variables = {}
        self.constants = {}
        self.next_var_address = 0x0000
        self.needs_mul = False
        self.needs_div = False
        self.label_count = 0
        self.loop_end_labels = []
        self.assembly = []

    def new_label(self, prefix):
        label = f"{prefix}_{self.label_count}"
        self.label_count += 1
        return label

    def generate(self, node):
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception(f"No visit_{type(node).__name__} method defined!")

    def visit_list(self, nodes):
        for node in nodes:
            self.generate(node)
        return self.assembly

    def visit_Block(self, node):
        for stmt in node.statements:
            self.generate(stmt)

    def visit_Number(self, node):
        self.assembly.append(f"    LDA #0x{node.value:02X}")

    def visit_Identifier(self, node):
        self.assembly.append(f"    LDA {node.name}")

    def visit_BinOp(self, node):
        if node.op in ('+', '-'):
            self.generate(node.left)
            self.assembly.append("    PUSH")
            self.generate(node.right)
            self.assembly.append("    TAB")
            self.assembly.append("    POP")
            if node.op == '+':
                self.assembly.append("    ADD B")
            elif node.op == '-':
                self.assembly.append("    SUB B")
        elif node.op == '*':
            self.needs_mul = True
            self.generate(node.left)
            self.assembly.append("    PUSH")
            self.generate(node.right)
            self.assembly.append("    TAB")
            self.assembly.append("    POP")
            self.assembly.append("    CALL __sys_mul")
        # TODO: Implement division
        elif node.op == '/':
            self.needs_div = True
            raise NotImplementedError("Division operation is not implemented yet.")
        elif node.op in ('==', '!='):
            label_true = self.new_label("__cmp_true")
            label_end = self.new_label("__cmp_end")
            self.generate(node.left)
            self.assembly.append("    PUSH")
            self.generate(node.right)
            self.assembly.append("    TAB")
            self.assembly.append("    POP")
            self.assembly.append("    SUB B")  # if they are equal, A becomes 0, setting Z flag
            if node.op == '==':
                self.assembly.append(f"    JZ {label_true}")
                self.assembly.append("    LDA #0x00")  # false
                self.assembly.append(f"    JMP {label_end}")
                self.assembly.append(f"{label_true}:")
                self.assembly.append("    LDA #0x01")  # true
                self.assembly.append(f"{label_end}:")
            elif node.op == '!=':
                self.assembly.append(f"    JZ {label_true}")
                self.assembly.append("    LDA #0x01")  # true
                self.assembly.append(f"    JMP {label_end}")
                self.assembly.append(f"{label_true}:")
                self.assembly.append("    LDA #0x00")  # false
                self.assembly.append(f"{label_end}:")

    def visit_Assign(self, node):
        self.generate(node.valueNode)
        self.assembly.append(f"    STA {node.targetName}")

    def visit_VarDecl(self, node):
        if node.name not in self.variables:
            self.variables[node.name] = self.next_var_address
            self.next_var_address += 1
            if self.next_var_address > 0x00FF:
                raise MemoryError("Zero Page RAM overflow!")

    def visit_ConstDecl(self, node):
        self.constants[node.name] = node.value

    def visit_IfStmt(self, node):
        label_false = self.new_label("__if_false")
        label_end = self.new_label("__if_end")

        self.generate(node.condition)

        self.assembly.append(f"    JZ {label_false}")
        for stmt in node.true_block:
            self.generate(stmt)

        self.assembly.append(f"    JMP {label_end}")

        self.assembly.append(f"{label_false}:")
        if node.false_block:
            for stmt in node.false_block:
                self.generate(stmt)
        self.assembly.append(f"{label_end}:")

    def visit_WhileStmt(self, node):
        label_start = self.new_label("__while_start")
        label_end = self.new_label("__while_end")
        
        self.loop_end_labels.append(label_end)

        self.assembly.append(f"{label_start}:")
        self.generate(node.condition)
        self.assembly.append(f"    JZ {label_end}")
        
        for stmt in node.body:
            self.generate(stmt)
            
        self.assembly.append(f"    JMP {label_start}")
        self.assembly.append(f"{label_end}:")
        
        self.loop_end_labels.pop()

    def visit_BreakStmt(self, node):
        if not self.loop_end_labels:
            raise Exception("Break statement used outside of loop!")
        label_end = self.loop_end_labels[-1]
        self.assembly.append(f"    JMP {label_end}")


def compile_file(input_file, output_file):
    with open(input_file, 'r') as f:
        code = f.read()

    lexer = CFlatLexer()
    parser = CFlatParser()
    codegen = CodeGenerator()

    ast_nodes = parser.parse(lexer.tokenize(code))
    if ast_nodes is None:
        print("\n[!] Compilation failed due to syntax errors shown above.")
        sys.exit(1)
    codegen.visit_list(ast_nodes)

    final_assembly = "    ORG 0x0200\n\n"

    final_assembly += "; --- Variables ---\n"
    equ_declarations = [f"{name} EQU 0x{addr:04X}" for name, addr in codegen.variables.items()]
    final_assembly += "\n".join(equ_declarations) + "\n\n"

    final_assembly += "; --- Main Code ---\n"
    final_assembly += "\n".join(codegen.assembly)
    final_assembly += "\n\n    HLT\n"

    final_assembly += "; --- Standard Library ---\n"
    if getattr(codegen, 'needs_mul', False): 
        final_assembly += """
    __sys_mul:
        JZ __mul_zero
        STA 0x00FC       ; Hardcoded temporary Zero Page address for MUL count
        LDA #0x00
        STA 0x00FD       ; Hardcoded temporary Zero Page address for MUL result
    __mul_loop:
        LDA 0x00FC
        JZ __mul_done
        DECA
        STA 0x00FC
        LDA 0x00FD
        ADD B
        STA 0x00FD
        JMP __mul_loop
    __mul_zero:
        LDA #0x00
        RET
    __mul_done:
        LDA 0x00FD
        RET
    """
    final_assembly += "\n; --- DB Constants ---\n"
    const_declarations = [f"{name}: DB 0x{val:02X}" for name, val in codegen.constants.items()]
    final_assembly += "\n".join(const_declarations) + "\n"

    with open(output_file, 'w') as f:
        f.write(final_assembly)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python compiler.py <input.cflat>")
        sys.exit(1)
        
    input_path = Path(sys.argv[1])
    output_path = input_path.with_suffix('.asm')
    
    compile_file(str(input_path), str(output_path))