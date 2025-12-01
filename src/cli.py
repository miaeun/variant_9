#!/usr/bin/env python3
import sys
from src import parser as p
from src import evaluator as ev
from src import xml_emit as xe

def main():
    if len(sys.argv) != 2:
        print("Usage: python -m src.cli <input-file>", file=sys.stderr)
        sys.exit(2)
    path = sys.argv[1]
    text = open(path, "r", encoding="utf-8").read()
    try:
        ast = p.parse_text(text)
    except Exception as e:
        print(f"Syntax error: {e}", file=sys.stderr)
        sys.exit(3)
    try:
        consts, out = ev.process_ast(ast)
    except Exception as e:
        print(f"Evaluation error: {e}", file=sys.stderr)
        sys.exit(4)
    xml = xe.emit_xml(out)
    print(xml)

if __name__ == "__main__":
    main()
