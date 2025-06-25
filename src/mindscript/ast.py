from enum import Enum
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel

# Optional[Token]s

TokenType = Enum(
    "TokenType",
    [
        "EOF",
        "HASH",
        "NULL",
        "STRING",
        "INTEGER",
        "NUMBER",
        "BOOLEAN",
        "OBJECT",
        "ARRAY",
        "FUNCTION",
        "ORACLE",
        "FROM",
        "TYPECONS",
        "TYPETYPE",
        "TYPE",
        "ENUM",
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
        "BANG",
        "ARROW",
        "ID",
        # "ADDRESS",
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
        "FOR",
        "IN",
        "RETURN",
        "BREAK",
        "CONTINUE",
    ]
)

Literal = Any


class Token(BaseModel):
    ttype: TokenType
    buffer: Optional[str] = ""
    index: Optional[int] = 0
    literal: Literal = None

    def __repr__(self):
        return f"{self.ttype.name}({self.buffer},{self.index}):{self.literal}"

    def __str__(self):
        return self.__repr__()


# Exceptions - Do not use these directly!
# Use auxiliary functions instead (e.g. error(msg) type functions.)

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
    operator: Optional[Token]
    expr: Expr

    def accept(self, visitor, **kwargs):
        return visitor.assign(self, **kwargs)


class Annotation(Expr):
    operator: Optional[Token]
    annotation: Optional[Token]
    expr: Expr

    def accept(self, visitor, **kwargs):
        return visitor.annotation(self, **kwargs)


class Declaration(Expr):
    operator: Optional[Token]
    token: Optional[Token]

    def accept(self, visitor, **kwargs):
        return visitor.declaration(self, **kwargs)


class Binary(Expr):
    left: Expr
    operator: Optional[Token]
    right: Expr

    def accept(self, visitor, **kwargs):
        return visitor.binary(self, **kwargs)


class Unary(Expr):
    operator: Optional[Token]
    expr: Expr

    def accept(self, visitor, **kwargs):
        return visitor.unary(self, **kwargs)


class Grouping(Expr):
    expr: Expr

    def accept(self, visitor, **kwargs):
        return visitor.grouping(self, **kwargs)


class Terminal(Expr):
    token: Optional[Token]

    def accept(self, visitor, **kwargs):
        return visitor.terminal(self, **kwargs)


class Array(Expr):
    array: List[Expr]

    def accept(self, visitor, **kwargs):
        return visitor.array(self, **kwargs)


class Map(Expr):
    map: Dict[str, Expr]

    def accept(self, visitor, **kwargs):
        return visitor.map(self, **kwargs)


class Block(Expr):
    exprs: List[Expr]

    def accept(self, visitor, **kwargs):
        return visitor.block(self, **kwargs)


class Conditional(Expr):
    operators: List[Token]
    conds: List[Expr]
    exprs: List[Expr]
    default: Optional[Expr]

    def accept(self, visitor, **kwargs):
        return visitor.conditional(self, **kwargs)


class For(Expr):
    operator: Optional[Token]
    target: Expr
    iterator: Expr
    expr: Expr

    def accept(self, visitor, **kwargs):
        return visitor.forloop(self, **kwargs)


class Call(Expr):
    operator: Optional[Token]
    expr: Expr
    arguments: List[Expr]

    def accept(self, visitor, **kwargs):
        return visitor.call(self, **kwargs)


class ObjectGet(Expr):
    operator: Optional[Token]
    expr: Expr
    index: Expr

    def accept(self, visitor, **kwargs):
        return visitor.object_get(self, **kwargs)


class ArrayGet(Expr):
    operator: Optional[Token]
    expr: Expr
    index: Expr

    def accept(self, visitor, **kwargs):
        return visitor.array_get(self, **kwargs)


class ObjectSet(Expr):
    operator: Optional[Token]
    expr: Expr
    index: Expr

    def accept(self, visitor, **kwargs):
        return visitor.object_get(self, **kwargs)


class ArraySet(Expr):
    operator: Optional[Token]
    expr: Expr
    index: Expr

    def accept(self, visitor, **kwargs):
        return visitor.array_get(self, **kwargs)


class Program(BaseModel):
    program: List[Expr]

    def accept(self, visitor, **kwargs):
        return visitor.program(self, **kwargs)


class TypeExpr(Expr):
    annotation: Optional[str] = None


class TypeDefinition(Expr):
    operator: Optional[Token] = None
    expr: TypeExpr

    def accept(self, visitor, **kwargs):
        return visitor.type_definition(self, **kwargs)


class TypeAnnotation(TypeExpr):
    operator: Optional[Token]
    annotation: Optional[Token]
    expr: Expr

    def accept(self, visitor, **kwargs):
        return visitor.type_annotation(self, **kwargs)


class TypeTerminal(TypeExpr):
    token: Token

    def accept(self, visitor, **kwargs):
        return visitor.type_terminal(self, **kwargs)


class TypeUnary(TypeExpr):
    operator: Optional[Token] = None
    expr: TypeExpr

    def accept(self, visitor, **kwargs):
        return visitor.type_unary(self, **kwargs)


class TypeBinary(TypeExpr):
    left: TypeExpr
    operator: Optional[Token]
    right: TypeExpr

    def accept(self, visitor, **kwargs):
        return visitor.type_binary(self, **kwargs)


class TypeEnum(TypeExpr):
    operator: Optional[Token]
    expr: Array
    values: Optional[Any] = None

    def accept(self, visitor, **kwargs):
        return visitor.type_enum(self, **kwargs)


class TypeArray(TypeExpr):
    expr: TypeExpr

    def accept(self, visitor, **kwargs):
        return visitor.type_array(self, **kwargs)


class TypeMap(TypeExpr):
    map: Dict[str, TypeExpr]
    required: Dict[str, bool]

    def accept(self, visitor, **kwargs):
        return visitor.type_map(self, **kwargs)


class TypeGrouping(TypeExpr):
    expr: TypeExpr

    def accept(self, visitor, **kwargs):
        return visitor.type_grouping(self, **kwargs)


class Function(Expr):
    operator: Optional[Token]
    parameters: List[Token]
    types: TypeBinary
    expr: Expr

    def accept(self, visitor, **kwargs):
        return visitor.function(self, **kwargs)


# Return

class Control(Exception):
    pass


class Return(Control):
    def __init__(self, operator: Optional[Token], expr: Expr):
        self.operator = operator
        self.expr = expr


class Break(Control):
    def __init__(self, operator: Optional[Token], expr: Expr):
        self.operator = operator
        self.expr = expr


class Continue(Control):
    def __init__(self, operator: Optional[Token], expr: Expr):
        self.operator = operator
        self.expr = expr


class Exit(Control):
    def __init__(self):
        pass
