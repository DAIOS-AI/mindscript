from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

# Tokens

TokenType = Enum(
    "TokenType",
    [
        "EOF",
        "SPACE",
        "UNDERSCORE",
        "HASH",
        "NULL",
        "INTEGER",
        "NUMBER",
        "BOOLEAN",
        "OBJECT",
        "ARRAY",
        "DATA_END",
        "LROUND",
        "CLROUND",
        "RROUND",
        "LCURLY",
        "RCURLY",
        "LSQUARE",
        "CLSQUARE",
        "RSQUARE",
        "EQ",
        "NEQ",
        "ASSIGN",
        "GREATER",
        "GREATER_EQ",
        "LESS",
        "LESS_EQ",
        "PLUS",
        "MINUS",
        "MULT",
        "DIV",
        "MOD",
        "PERIOD",
        "COMMA",
        "COLON",
        "QUESTION",
        "ARROW",
        "WORD_LIKE",
        "STRING",
        "ID",
        "ADDRESS",
        "NOT",
        "AND",
        "OR",
        "LET",
        "DO",
        "END",
        "IF",
        "THEN",
        "ELIF",
        "ELSE",
        "WHILE",
        "FOR",
        "IN",
        "RETURN",
        "BREAK",
        "CONTINUE",
        "TYPE",
        "FUNCTION",
    ]
)

Literal = Any


class Token(BaseModel):
    ttype: TokenType
    col: int = 0
    line: int = 0
    literal: Literal = None

    def __repr__(self):
        return f"{self.ttype.name}({self.line},{self.col}):{self.literal}"

    def __str__(self):
        return self.__repr__()

# Exceptions

   
class IncompleteExpression(Exception):
    def __init__(self):
        pass


class LexicalError(Exception):
    def __init__(self, message):
        super().__init__(message)


class SyntaxError(Exception):
    def __init__(self, message):
        super().__init__(message)


class RuntimeError(Exception):
    def __init__(self, message):
        super().__init__(message)

# AST Nodes


class Expr(BaseModel):
    pass


class Assign(Expr):
    target: Expr
    operator: Token
    expr: Expr

    def accept(self, visitor):
        return visitor.assign(self)


class Annotation(Expr):
    operator: Token
    comment: Token
    expr: Expr

    def accept(self, visitor):
        return visitor.annotation(self)


class Declaration(Expr):
    operator: Token
    token: Token

    def accept(self, visitor):
        return visitor.declaration(self)


class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr

    def accept(self, visitor):
        return visitor.binary(self)


class Unary(Expr):
    operator: Token
    expr: Expr

    def accept(self, visitor):
        return visitor.unary(self)


class Grouping(Expr):
    expr: Expr

    def accept(self, visitor):
        return visitor.grouping(self)


class Terminal(Expr):
    token: Token

    def accept(self, visitor):
        return visitor.terminal(self)


class Array(Expr):
    array: List[Expr]

    def accept(self, visitor):
        return visitor.array(self)


class Map(Expr):
    map: Dict[str, Expr]

    def accept(self, visitor):
        return visitor.map(self)


class Block(Expr):
    exprs: List[Expr]

    def accept(self, visitor):
        return visitor.block(self)


class Conditional(Expr):
    operators: List[Token]
    conds: List[Expr]
    exprs: List[Expr]
    default: Optional[Expr]

    def accept(self, visitor):
        return visitor.conditional(self)


class For(Expr):
    operator: Token
    target: Expr
    iterator: Expr
    expr: Expr

    def accept(self, visitor):
        return visitor.forloop(self)


class Call(Expr):
    expr: Expr
    operator: Token
    arguments: List[Expr]

    def accept(self, visitor):
        return visitor.call(self)


class Get(Expr):
    operator: Token
    expr: Expr
    index: Expr

    def accept(self, visitor):
        return visitor.get(self)


class Set(Expr):
    operator: Token
    expr: Expr
    index: Expr

    def accept(self, visitor):
        return visitor.get(self)


class Function(Expr):
    operator: Token
    out_type: Expr
    parameters: List[Token]
    param_types: List[Expr]
    expr: Expr

    def accept(self, visitor):
        return visitor.function(self)


class Program(BaseModel):
    program: List[Expr]

    def accept(self, visitor):
        return visitor.program(self)

# Return

class Return(Exception):
    def __init__(self, operator: Token, expr: Expr):
        self.operator = operator
        self.expr = expr

