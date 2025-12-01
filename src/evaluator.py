from xml.etree.ElementTree import Element, SubElement, tostring
from typing import Any, Dict, List

# Evaluator handles constant declarations and constant-expression evaluation
class EvalError(Exception):
    pass

def eval_expr(node, consts: Dict[str, Any]):
    t = node[0]
    if t == "number":
        return node[1]
    if t == "string":
        return node[1]
    if t == "array":
        return [eval_expr(v, consts) for v in node[1]]
    if t == "var":
        name = node[1]
        if name in consts:
            return consts[name]
        raise EvalError(f"Unknown name '{name}' in expression")
    if t == "binop":
        op = node[1]; a = eval_expr(node[2], consts); b = eval_expr(node[3], consts)
        if op == "+": return a + b
        if op == "-": return a - b
        if op == "*": return a * b
        if op == "/": 
            if b == 0: raise EvalError("division by zero")
            return a // b if isinstance(a,int) and isinstance(b,int) else a / b
    if t == "call":
        name = node[1]; args = [eval_expr(a, consts) for a in node[2]]
        if name == "mod":
            if len(args)!=2: raise EvalError("mod expects 2 args")
            return args[0] % args[1]
        if name == "sort":
            if len(args)!=1: raise EvalError("sort expects 1 arg")
            return sorted(args[0])
        # allow other functions but error by default
        raise EvalError(f"Unknown function '{name}'")
    raise EvalError(f"Unsupported node {node}")

def process_ast(ast):
    consts = {}
    output_nodes = []
    for stmt in ast:
        if stmt[0] == "const_decl":
            name = stmt[1]; valnode = stmt[2]
            # if const node is const_expr then evaluate
            if isinstance(valnode, tuple) and valnode[0]=="const_expr":
                value = eval_expr(valnode[1], consts)
            else:
                value = eval_expr(valnode, consts)
            consts[name] = value
            output_nodes.append(("const", name, value))
        else:
            # value stmt (emit)
            value = eval_expr(stmt, consts)
            output_nodes.append(("value", value))
    return consts, output_nodes

