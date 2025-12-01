from lark import Lark, Transformer, v_args, Token
import re

GRAMMAR = open("grammar.lark", "r", encoding="utf-8").read()

# remove multi-line comments #= ... =# before parsing
def strip_comments(text: str) -> str:
    return re.sub(r"#=[\\s\\S]*?=#", "", text)

parser = Lark(GRAMMAR, start="start", parser="lalr")

@v_args(inline=True)
class ASTBuilder(Transformer):
    def __init__(self):
        self.consts = {}

    def program(self, *stmts):
        return list(stmts)

    def const_decl(self, name, value):
        return ("const_decl", str(name), value)

    def const_expr(self, expr):
        return ("const_expr", expr)

    def array(self, *vals):
        # vals: possibly single list node
        if len(vals)==1 and isinstance(vals[0], list):
            return ("array", vals[0])
        if len(vals)==0:
            return ("array", [])
        # direct list
        return ("array", list(vals))

    def value_list(self, *vals):
        return list(vals)

    def string(self, token):
        s = token.value
        return ("string", eval(s))  # safe: uses Python string literal parser

    def BIN_INT(self, token):
        txt = token.value
        return ("number", int(txt[2:], 2))

    def var_ref(self, name):
        return ("var", str(name))

    def add(self, a, b):
        return ("binop", "+", a, b)

    def sub(self, a, b):
        return ("binop", "-", a, b)

    def mul(self, a, b):
        return ("binop", "*", a, b)

    def div(self, a, b):
        return ("binop", "/", a, b)

    def function_call(self, name, args=None):
        if args is None:
            args = []
        elif isinstance(args, list) and len(args)==1 and not isinstance(args[0], tuple):
            args = args
        return ("call", str(name), args)

def parse_text(text: str):
    text = strip_comments(text)
    tree = parser.parse(text)
    ast = ASTBuilder().transform(tree)
    return ast
