from collections import namedtuple
from enum import Enum
from abc import abstractmethod
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

# Tokens

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
        "TYPECONS",
        "TYPE",
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


class ObjectGet(Expr):
    operator: Token
    expr: Expr
    index: Expr

    def accept(self, visitor):
        return visitor.object_get(self)


class ArrayGet(Expr):
    operator: Token
    expr: Expr
    index: Expr

    def accept(self, visitor):
        return visitor.array_get(self)


class ObjectSet(Expr):
    operator: Token
    expr: Expr
    index: Expr

    def accept(self, visitor):
        return visitor.object_get(self)


class ArraySet(Expr):
    operator: Token
    expr: Expr
    index: Expr

    def accept(self, visitor):
        return visitor.array_get(self)


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


class TypeExpr(Expr):
    pass


class TypeDefinition(TypeExpr):
    operator: Token
    expr: TypeExpr

    def accept(self, visitor):
        return visitor.type_definition(self)


class TypeAnnotation(TypeExpr):
    operator: Token
    comment: Token
    expr: Expr

    def accept(self, visitor):
        return visitor.type_annotation(self)


class TypeTerminal(TypeExpr):
    token: Token

    def accept(self, visitor):
        return visitor.type_terminal(self)


class TypeUnary(TypeExpr):
    operator: Token
    expr: TypeExpr

    def accept(self, visitor):
        return visitor.type_unary(self)


class TypeBinary(TypeExpr):
    left: TypeExpr
    operator: Token
    right: TypeExpr

    def accept(self, visitor):
        return visitor.type_binary(self)


class TypeArray(TypeExpr):
    array: List[TypeExpr]

    def accept(self, visitor):
        return visitor.type_array(self)


class TypeMap(TypeExpr):
    map: Dict[str, TypeExpr]

    def accept(self, visitor):
        return visitor.type_map(self)


class TypeGrouping(TypeExpr):
    expr: TypeExpr

    def accept(self, visitor):
        return visitor.type_grouping(self)

# Return

class Control(Exception):
    pass


class Return(Control):
    def __init__(self, operator: Token, expr: Expr):
        self.operator = operator
        self.expr = expr


class Break(Control):
    def __init__(self, operator: Token, expr: Expr):
        self.operator = operator
        self.expr = expr


class Continue(Control):
    def __init__(self, operator: Token, expr: Expr):
        self.operator = operator
        self.expr = expr


# Value types

# Primitive value.
class Value():
    value: any
    comment: str

    def __init__(self, value, comment=None):
        self.value = value
        self.comment = comment


# Types.


class UserType():
    definition: Expr

    def __init__(self, ip: 'Interpreter', definition: TypeExpr):  # type: ignore
        self.ip = ip
        self.env = ip.env
        self.definition = definition

    def __expr__(self):
        text = self.ip.printer.print(self.definition)
        return text

    def __str__(self):
        text = self.ip.printer.print(self.definition)
        return text


# Callables.


class Callable():
    definition: Expr

    @abstractmethod
    def call(self, ip: 'Interpreter', args: List[Any]) -> Any:  # type: ignore
        pass


# Native functions.

class NativeCallable(Callable):
    def __init__(self, ip: 'Interpreter'):  # type: ignore
        self.ip = ip
        self.env = ip.env
        self.definition = Terminal(
            token=Token(
                ttype=TokenType.STRING,
                literal="<native function>"
            )
        )

    @abstractmethod
    def call(self, args: List[Any]) -> Any:
        pass

    def __repr__(self):
        return "<native function>"

    def __str__(self):
        return "<native function>"
