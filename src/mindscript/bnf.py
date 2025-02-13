import re
import mindscript.ast as ast
from mindscript.objects import MType
from pydantic import BaseModel

# GRAMMAR = r"""
# # BNF grammar to parse JSON objects
# root   ::= ws object
# value  ::= object | array | string | number | ("true" | "false" | "null")

# object ::=
#   "{" ws (
#             string ":" ws value ws
#     ("," ws string ":" ws value ws )*
#   )? "}"

# array  ::=
#   "[" ws (
#             value ws
#     ("," ws value ws )*
#   )? "]"

# string ::=
#   "\"" (
#     [^"\\] |
#     "\\" (["\\/bfnrt] | "u" [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F]) # escapes
#   )* "\""

# number ::= ("-"? ([0-9] | [1-9] [0-9]*)) ("." [0-9]+)? ([eE] [-+]? [0-9]+)?

# # whitespace
# ws ::= ([ \t\n] ws)?
# """

GRAMMAR_EXT = r"""
root        ::= ws chunk ws "end"
chunk       ::= control (ws control)*
control     ::= ("return"|"break"|"continue") "(" ws expression ws ")" | expression
expression  ::= ("#" ws string ws)? assignment
assignment  ::= binary ws "=" ws expression | binary
binary      ::= unary (ws ("and"|"or"|"=="|"!="|"<"|"<="|">"|">="|"+"|"-"|"*"|"/"|"%") ws binary)*
unary       ::= (("not"|"-") ws)? call
call        ::= primary ( "(" ws arglist ws ")" | "." identifier | "[" ws expression ws "]" )*
arglist     ::= (expression (ws "," ws expression)*)?
primary     ::= integer | number | string | boolean | "null" | 
                array | map | type | function | target | "(" ws expression ws ")" | 
                block | conditional | forloop
array       ::= "[" ws arglist ws "]"
map         ::= "{" ws itemlist ws "}"
itemlist    ::= identifier ws ":" ws expression (ws identifier ws ":" expression)*
block       ::= "do" ws chunk ws "end"
conditional ::= ("if" ws expression ws "then" ws chunk ws
                ("elif" ws expression ws "then" ws chunk ws)*
                ("else" ws chunk ws)? "end")
forloop     ::= "for" ws expression ws "in" ws expression ws block
target      ::= ("let" ws)? identifier
function    ::= "fun(" ws paramlist ws ")" (ws "->" ws typeexpr)? ws block
paramlist   ::= (identifier ws ":" ws typeexpr (ws identifier ws ":" ws typeexpr)*)?
type        ::= "type" ws typeexpr
typeexpr    ::= typeunary (ws "->" ws typeexpr)?
typeunary   ::= typeprim ("?")?
typeprim    ::= identifier | typeterm | typearr | typemap | "(" ws typeexpr ws ")"
typearr     ::= "[" ws (typeexpr (ws "," ws typeexpr)*)? ws "]"
typemap     ::= "{" ws (identifier ws ":" ws typeexpr (ws "," ws identifier ws ":" ws typeexpr)*)? ws "}"
typeterm    ::= "Null" | "Bool" | "Int" | "Num" | "Str" | "Any"
boolean     ::= "true" | "false"
string      ::=
  "\"" (
    [^"\\] |
    "\\" (["\\/bfnrt] | "u" [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F]) # escapes
  )* "\""
integer     ::= "-"? ([0-9] | [1-9] [0-9]*)
number      ::= ("-"? ([0-9] | [1-9] [0-9]*)) "." [0-9]* ([eE] [-+]? [0-9]+)?
ws          ::= ([ \t\n] ws)?
identifier  ::= [_a-zA-Z] [_a-zA-Z0-9]*
"""

GRAMMAR = r"""
boolean     ::= "true" | "false"
string      ::=
  "\"" (
    [^"\\] |
    "\\" (["\\/bfnrt] | "u" [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F]) # escapes
  )* "\""
integer     ::= "-"? ([0-9] | [1-9] [0-9]*)
number      ::= ("-"? ([0-9] | [1-9] [0-9]*)) "." [0-9]* ([eE] [-+]? [0-9]+)?
ws          ::= ([ \t\n] ws)?
identifier  ::= [_a-zA-Z] [_a-zA-Z0-9]*
"""

GRAMMAR_EXTENDED = r"""
# "A variable definition."
let x = 0

# "A calculation."
let y = (4 * 16) / 3.14 % 10

# "Defining a type with a mandatory name and an optional age."
let MyType = type {name: Str, age: Int?}

# "Defining a function."
let factorial = fun(number: Int) -> Int do
    if n == 0 then
        return(1)
    elif n == 1 then
        return(1)
    else
        return( n * factorial(n-1) )
    end
end

# "Calling a function."
let result = factorial(10)
"""


class BNFRule(BaseModel):
    id: str
    rule: str


class BNFFormatter():

    def __init__(self, interpreter):
        self.interpreter = interpreter

    # TODO: Rewrites memory addresses as 5 digit hexadecimals - it won't guarantee uniqueness.
    def tag(self, obj):
        return hex(id(obj) % 99989)[2:]

    def type_definition(self, node, env=None, ids=None):
        # Should not be called!
        raise ValueError("type_definition should not be called!")

    def type_annotation(self, node, env=None, ids=None):
        # Should not be called!
        raise ValueError("type_annotation should not be called!")

    def _resolve_type(self, t, env, ids=None):
        resolving = True
        while resolving:
            if isinstance(t, ast.TypeAnnotation):
                t = t.expr
            elif isinstance(t, ast.TypeGrouping):
                t = t.expr
            elif isinstance(t, ast.TypeTerminal) and t.token.ttype == ast.TokenType.ID:
                key = t.token.literal
                value = env.get(key)
                if type(value) != MType:
                    raise ValueError(f"Referencing '{key}', which is not a type.")
                t = value.definition
                env = value.environment
            else:
                resolving = False
        return [t, env]

    # TODO: Solve for references.
    def type_terminal(self, node, env=None, ids=None):

        if node.token.ttype == ast.TokenType.ID:
            new_node, new_env = self._resolve_type(node, env)
            return new_node.accept(self, env=new_env, ids=ids)
        
        if node.token.ttype == ast.TokenType.TYPE:
            if node.token.literal == "Int":
                term = 'integer'
            elif node.token.literal == "Num":
                term = 'number'
            elif node.token.literal == "Str":
                term = 'string'
            elif node.token.literal == "Bool":
                term = 'boolean'
            elif node.token.literal == "Null":
                term = '"null"'
            elif node.token.literal == "Any":
                term = '("null" | boolean | integer | number | string | array | object)'
            else:
                raise ValueError(f"Unknown terminal type '{node.token.literal}'.")
            head = term
            body = ''
            if node.annotation is not None:
                head = f'terminal{self.tag(node)}'
                body = f'# {node.annotation}\n{head} ::= {term}\n'
            return BNFRule(id=head, rule=body)

        raise ValueError("Unknown type!")

    def type_grouping(self, node, env=None, ids=None):
        return node.expr.accept(self, env=env, ids=ids)

    def type_unary(self, node, env=None, ids=None):
        head = f'optional{self.tag(node)}'
        if id(node) in ids: return BNFRule(id=head, rule='')
        else: ids[id(node)] = True

        sub = node.expr.accept(self, env=env, ids=ids)
        body = f'{head} ::= "null" | {sub.id}\n{sub.rule}'
        return BNFRule(id=head, rule=body)
    
    # TODO
    def type_binary(self, node, env=None, ids=None):
        head = f'binary{self.tag(node)}'
        if id(node) in ids: return BNFRule(id=head, rule='')
        else: ids[id(node)] = True
        raise NotImplementedError("BNF grammars for function types are not implemented yet.")
    
    def type_enum(self, node, env=None, ids=None):
        head = f'enum{self.tag(node)}'
        if id(node) in ids: return BNFRule(id=head, rule='')
        else: ids[id(node)] = True

        subs = []
        for expr in node.values.value:
            txt = self.interpreter.printer.print(expr)
            txt = self.interpreter.printer.shorten(txt)
            txt = r'"' + re.sub(r'"', r'\"', txt) + r'"'
            subs.append(txt)
        body = f'{head} ::= ' + '| '.join(subs)
        return BNFRule(id=head, rule=body)

    def type_array(self, node, env=None, ids=None):
        head = f'array{self.tag(node)}'
        if id(node) in ids: return BNFRule(id=head, rule='')
        else: ids[id(node)] = True

        sub = node.expr.accept(self, env=env, ids=ids)
        body = f'{head} ::= "[" ws ({sub.id})? (ws "," ws {sub.id})* ws "]"\n' + sub.rule
        return BNFRule(id=head, rule=body)

    def type_map(self, node, env=None, ids=None):
        head = f'object{self.tag(node)}'
        if id(node) in ids: return BNFRule(id=head, rule='')
        else: ids[id(node)] = True

        keys = []
        subs = []
        for key, expr in node.map.items():
            keys.append(key)
            subs.append(expr.accept(self, env=env, ids=ids))
        
        key, sub = keys[0], subs[0]
        items = r'"{" ws "\"' + key + r'\"" ws ":" ws ' + sub.id
        for key, sub in zip(keys[1:], subs[1:]):
            items += r' ws "," ws "\"' + key + r'\"" ws ":" ws ' + sub.id
        items += r' ws "}"'

        body = head + ' ::= ( ' + items + ' )\n' 
        body += "".join([sub.rule for sub in subs])

        return BNFRule(id=head, rule=body)

    def format(self, value):
        # print(f"BNFFormatter.format: value.definition = {value.definition}")
        if type(value) != MType:
            return None
        bnf = value.definition.accept(self, env=value.environment, ids=dict())
        grammar = f'root ::= {bnf.id}\n{bnf.rule}' + GRAMMAR
        # print("Grammar:\n" + repr(grammar))
        return grammar