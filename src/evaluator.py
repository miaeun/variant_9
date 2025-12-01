from typing import Any, Dict

class EvalError(Exception):
    pass

def eval_expr(node, consts: dict):
    if isinstance(node, tuple):
        t = node[0]

        if t == "number" or t == "string":
            return node[1]

        if t == "array":
            return [eval_expr(v, consts) for v in node[1]]

        if t == "var":
            name = node[1]
            if name in consts:
                return consts[name]
            raise EvalError(f"Unknown name '{name}'")

        if t == "const_expr":
            return eval_expr(node[1], consts)

        if t == "binop":
            op = node[1]
            a = eval_expr(node[2], consts)
            b = eval_expr(node[3], consts)

            def apply_op(x, y):
                if op == "+": return x + y
                if op == "-": return x - y
                if op == "*": return x * y
                if op == "/": return x // y if isinstance(x,int) and isinstance(y,int) else x / y

            # поддержка массивов + числа / массивы + массивы
            if isinstance(a, list) and isinstance(b, list):
                return [apply_op(x, y) for x, y in zip(a, b)]
            if isinstance(a, list):
                return [apply_op(x, b) for x in a]
            if isinstance(b, list):
                return [apply_op(a, y) for y in b]
            return apply_op(a, b)

        if t == "call":
            name = node[1]
            args = [eval_expr(a, consts) for a in node[2]]
            if name == "mod":
                if len(args) != 2: raise EvalError("mod expects 2 args")
                return args[0] % args[1]
            if name == "sort":
                if len(args) != 1: raise EvalError("sort expects 1 arg")
                return sorted(args[0])
            raise EvalError(f"Unknown function '{name}'")

        raise EvalError(f"Unsupported node {node}")

    # Если пришёл Tree (редкий случай)
    from lark import Tree
    if isinstance(node, Tree):
        # Попробуем рекурсивно обрабатывать детей
        if len(node.children) == 1:
            return eval_expr(node.children[0], consts)
        return [eval_expr(c, consts) for c in node.children]

    # Любой другой тип
    return node

def process_ast(ast):
    consts = {}
    output_nodes = []

    for stmt in ast:
        if stmt[0] == "const_decl":
            name = stmt[1]
            valnode = stmt[2]
            if isinstance(valnode, tuple) and valnode[0] == "const_expr":
                value = eval_expr(valnode[1], consts)
            else:
                value = eval_expr(valnode, consts)
            consts[name] = value
            output_nodes.append(("const", name, value))
        else:
            value = eval_expr(stmt, consts)
            output_nodes.append(("value", value))

    return consts, output_nodes
