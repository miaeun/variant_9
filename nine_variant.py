#!/usr/bin/env python3
import sys, re, argparse
import xml.etree.ElementTree as ET
from typing import List, Dict, Any

#---------------- Токены ----------------
TOKEN_SPEC = [
    ("MLC_START", r"#="),
    ("MLC_END", r"=#"),
    ("FUNC", r"\b(mod|sort)\b"),
    ("NUMBER", r"0[bB][01]+"),
    ("NAME", r"[a-zA-Z]+"),
    ("STRING", r'"(?:[^"\\]|\\.)*"'),
    ("LBRACE", r"\(\{"),
    ("RBRACE", r"\}\)"),
    ("COMMA", r","),
    ("ASSIGN", r"<-"),
    ("CEXPR_START", r"\^\["),
    ("CEXPR_END", r"\]"),
    ("LPAREN", r"\("),
    ("RPAREN", r"\)"),
    ("PLUS", r"\+"),
    ("MINUS", r"-"),
    ("TIMES", r"\*"),
    ("DIV", r"/"),
    ("WS", r"[ \t\r\n]+"),
]
TOKEN_RE = re.compile("|".join(f"(?P<{n}>{p})" for n, p in TOKEN_SPEC))

class Token:
    def __init__(self, typ, val, pos): self.type,self.val,self.pos=typ,val,pos
    def __repr__(self): return f"Token({self.type},{self.val},{self.pos})"

def lex(text: str) -> List[Token]:
    pos = 0; tokens=[]; in_mlc=False
    while pos < len(text):
        m=TOKEN_RE.match(text,pos)
        if not m:
            if in_mlc:
                end = text.find('=#',pos)
                if end==-1: raise Exception(f"Unterminated MLC at {pos}")
                pos=end+2; in_mlc=False; continue
            raise Exception(f"Illegal char at {pos}: {text[pos]!r}")
        typ = m.lastgroup; val = m.group(typ)
        if typ=="MLC_START":
            end=text.find("=#",m.end())
            if end==-1: raise Exception(f"Unterminated MLC at {m.start()}")
            pos=end+2; continue
        if typ=="WS": pos=m.end(); continue
        tokens.append(Token(typ,val,m.start()))
        pos=m.end()
    return tokens

#---------------- AST ----------------
class ASTValue: pass
class ASTNumber(ASTValue): 
    def __init__(self,text): self.text=text
class ASTString(ASTValue):
    def __init__(self,text): self.text=bytes(text[1:-1],"utf-8").decode("unicode_escape")
class ASTArray(ASTValue):
    def __init__(self,items): self.items=items
class ASTName(ASTValue):
    def __init__(self,name): self.name=name
class ASTConstExpr(ASTValue):
    def __init__(self,tokens): self.tokens=tokens
class Decl:
    def __init__(self,name,value): self.name=name; self.value=value

#---------------- Парсер ----------------
class Parser:
    def __init__(self,tokens): self.tokens=tokens; self.pos=0
    def at(self): return self.tokens[self.pos] if self.pos<len(self.tokens) else None
    def eat(self,typ=None):
        t=self.at()
        if not t: raise Exception("Unexpected EOF")
        if typ and t.type!=typ: raise Exception(f"Expected {typ}, got {t.type} at {t.pos}")
        self.pos+=1; return t
    def parse(self) -> List[Decl]:
        decls=[]
        while self.at(): decls.append(self.parse_decl())
        return decls
    def parse_decl(self) -> Decl:
        t=self.eat("NAME"); name=t.val
        self.eat("ASSIGN")
        value=self.parse_value()
        return Decl(name,value)
    def parse_value(self) -> ASTValue:
        t=self.at()
        if t.type=="NUMBER": self.eat("NUMBER"); return ASTNumber(t.val)
        if t.type=="STRING": self.eat("STRING"); return ASTString(t.val)
        if t.type=="LBRACE": return self.parse_array()
        if t.type=="CEXPR_START": return self.parse_const_expr()
        if t.type=="NAME": self.eat("NAME"); return ASTName(t.val)
        if t.type=="FUNC": self.eat("FUNC"); return ASTName(t.val)
        raise Exception(f"Unexpected token {t}")
    def parse_array(self) -> ASTArray:
        self.eat("LBRACE"); items=[]
        while True:
            if self.at().type=="RBRACE": self.eat("RBRACE"); break
            items.append(self.parse_value())
            if self.at() and self.at().type=="COMMA": self.eat("COMMA"); continue
        return ASTArray(items)
    def parse_const_expr(self) -> ASTConstExpr:
        self.eat("CEXPR_START"); toks=[]
        while True:
            t=self.at()
            if not t: raise Exception("Unterminated const expr")
            if t.type=="CEXPR_END": self.eat("CEXPR_END"); break
            toks.append(t); self.pos+=1
        return ASTConstExpr(toks)

#---------------- Вычисление ----------------
OP_INFO={'+':(1,'L'),'-':(1,'L'),'*':(2,'L'),'/':(2,'L')}

def tokens_to_rpn(tokens):
    output=[]; stack=[]
    for t in tokens:
        if t.type in ("NUMBER","STRING","NAME","LBRACE"): output.append(t)
        elif t.type in ("PLUS","MINUS","TIMES","DIV"):
            while stack and stack[-1].type in ("PLUS","MINUS","TIMES","DIV"):
                top=stack[-1].val
                if (OP_INFO[top][0]>OP_INFO[t.val][0]) or (OP_INFO[top][0]==OP_INFO[t.val][0] and OP_INFO[t.val][1]=='L'):
                    output.append(stack.pop())
                else: break
            stack.append(t)
        elif t.type=="FUNC": stack.append(t)
        elif t.type=="LPAREN": stack.append(t)
        elif t.type=="RPAREN":
            while stack and stack[-1].type!="LPAREN": output.append(stack.pop())
            stack.pop()
            if stack and stack[-1].type=="FUNC": output.append(stack.pop())
        elif t.type=="COMMA":
            while stack and stack[-1].type!="LPAREN": output.append(stack.pop())
    while stack: output.append(stack.pop())
    return output

def eval_rpn(rpn,consts):
    st=[]
    for t in rpn:
        if t.type=="NUMBER": st.append(int(t.val[2:],2))
        elif t.type=="STRING": st.append(bytes(t.val[1:-1],'utf-8').decode('unicode_escape'))
        elif t.type=="LBRACE":
            content=t.val[2:-2]; parts=[p.strip() for p in content.split(',') if p.strip()]
            vals=[]
            for p in parts:
                if p.startswith("0b"): vals.append(int(p[2:],2))
                elif p.startswith('"'): vals.append(bytes(p[1:-1],'utf-8').decode('unicode_escape'))
                elif p in consts: vals.append(consts[p])
                else: raise Exception(f"Unknown value {p}")
            st.append(vals)
        elif t.type=="NAME":
            if t.val in consts: st.append(consts[t.val])
            else: raise Exception(f"Unknown name {t.val}")
        elif t.type in ("PLUS","MINUS","TIMES","DIV"):
            b=st.pop(); a=st.pop()
            st.append(a+b if t.type=="PLUS" else a-b if t.type=="MINUS" else a*b if t.type=="TIMES" else a//b)
        elif t.type=="FUNC":
            if t.val=="mod": b=st.pop(); a=st.pop(); st.append(a%b)
            elif t.val=="sort": a=st.pop(); st.append(sorted(a))
    if len(st)!=1: raise Exception("Expression did not reduce to single value")
    return st[0]

def eval_value(v,consts):
    if isinstance(v,ASTNumber): return int(v.text[2:],2)
    if isinstance(v,ASTString): return v.text
    if isinstance(v,ASTArray): return [eval_value(it,consts) for it in v.items]
    if isinstance(v,ASTName):
        if v.name in consts: return consts[v.name]
        raise Exception(f"Unknown name {v.name}")
    if isinstance(v,ASTConstExpr): return eval_rpn(tokens_to_rpn(v.tokens), consts)
    raise Exception("Unsupported AST value")

def evaluate_decl(decl,consts):
    consts[decl.name]=eval_value(decl.value,consts)

#---------------- XML ----------------
def indent_xml(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        for child in elem:
            indent_xml(child, level+1)
        if not child.tail or not child.tail.strip():
            child.tail = i
    else:
        if not elem.text or not elem.text.strip():
            elem.text = ''
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def append_value_xml(parent,v,consts):
    if isinstance(v,ASTNumber): e=ET.SubElement(parent,"number"); e.text=str(int(v.text[2:],2))
    elif isinstance(v,ASTString): e=ET.SubElement(parent,"string"); e.text=v.text
    elif isinstance(v,ASTArray):
        e=ET.SubElement(parent,"array")
        for it in v.items: it_el=ET.SubElement(e,"item"); append_value_xml(it_el,it,consts)
    elif isinstance(v,ASTName):
        if v.name in consts: e=ET.SubElement(parent,"constexpr"); e.text=str(consts[v.name])
        else: e=ET.SubElement(parent,"name"); e.text=v.name
    elif isinstance(v,ASTConstExpr):
        try: val=eval_rpn(tokens_to_rpn(v.tokens),consts)
        except Exception as ex: val=f"<error>{ex}</error>"
        e=ET.SubElement(parent,"constexpr"); e.text=str(val)

def to_xml(decls,consts):
    root=ET.Element("config")
    for d in decls:
        el=ET.SubElement(root,"decl",name=d.name)
        append_value_xml(el,d.value,consts)
    indent_xml(root)
    return ET.tostring(root,encoding="unicode")

#---------------- Основные функции ----------------
def process(text):
    tokens=lex(text)
    parser=Parser(tokens)
    decls=parser.parse()
    consts={}
    for d in decls: evaluate_decl(d,consts)
    return to_xml(decls,consts),consts

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("-i","--input",required=True)
    args=ap.parse_args()
    with open(args.input,'r',encoding='utf-8') as f: text=f.read()
    try:
        xml,consts=process(text)
        print(xml)
    except Exception as e:
        print(f"Error: {e}",file=sys.stderr); sys.exit(2)

if __name__=="__main__": main()
