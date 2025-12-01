from lark import Lark, Transformer, v_args, Token, Tree
import re

GRAMMAR = open("grammar.lark", "r", encoding="utf-8").read()

def strip_comments(text: str) -> str:
    return re.sub(r"#=[\s\S]*?=#", "", text)

parser = Lark(GRAMMAR, start="start", parser="lalr")

@v_args(inline=True)
class ASTBuilder(Transformer):
    def program(self, *stmts):
        return list(stmts)

    def const_decl(self, name, value):
        return ("const_decl", str(name), value)

    # ---------- VALUES ----------
    def string(self, token):
        return ("string", eval(token.value))

    def BIN_INT(self, token):
        return ("number", int(token.value[2:], 2))

    def var_ref(self, name):
        return ("var", str(name))

    # ---------- ARRAYS ----------
    def array(self, items=None):
        if items is None:
            return ("array", [])
        if isinstance(items, Tree):
            return ("array", self.value_list(*items.children))
        if isinstance(items, list):
            return ("array", items)
        return ("array", [items])

    def value_list(self, *vals):
        return list(vals)

    # ---------- EXPRESSIONS ----------
    def const_expr(self, expr):
        return ("const_expr", expr)

    def add(self, a, b):
        return ("binop", "+", a, b)

    def sub(self, a, b):
        return ("binop", "-", a, b)

    def mul(self, a, b):
        return ("binop", "*", a, b)

    def div(self, a, b):
        return ("binop", "/", a, b)

    def function_call(self, name, args=None):
        if isinstance(name, Token):
            name = name.value
        if args is None:
            args = []
        elif isinstance(args, Tree):
            args = self.value_list(*args.children)
        elif not isinstance(args, list):
            args = [args]
        return ("call", str(name), args)

def parse_text(text: str):
    text = strip_comments(text)
    tree = parser.parse(text)
    ast = ASTBuilder().transform(tree)
    # Рекурсивно разворачиваем все оставшиеся Tree
    def unwrap(node):
        if isinstance(node, Tree):
            if len(node.children) == 1:
                return unwrap(node.children[0])
            return [unwrap(c) for c in node.children]
        elif isinstance(node, list):
            return [unwrap(c) for c in node]
        else:
            return node
    return unwrap(ast)
