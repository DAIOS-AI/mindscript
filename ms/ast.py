from collections import namedtuple
from enum import Enum
from abc import abstractmethod
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
        "TYPECONS",
        "TYPETYPE",
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
    col: Optional[int] = 0
    line: Optional[int] = 0
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

class TypeError(Exception):
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
    comment: Optional[Token]
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
    expr: Expr
    operator: Optional[Token]
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
    pass


class TypeDefinition(TypeExpr):
    operator: Optional[Token] = None
    expr: TypeExpr

    def accept(self, visitor, **kwargs):
        return visitor.type_definition(self, **kwargs)


class TypeAnnotation(TypeExpr):
    operator: Optional[Token]
    comment: Optional[Token]
    expr: Expr

    def accept(self, visitor, **kwargs):
        return visitor.type_annotation(self, **kwargs)


class TypeTerminal(TypeExpr):
    token: Optional[Token]

    def accept(self, visitor, **kwargs):
        return visitor.type_terminal(self, **kwargs)


class TypeUnary(TypeExpr):
    operator: Optional[Token]
    expr: TypeExpr

    def accept(self, visitor, **kwargs):
        return visitor.type_unary(self, **kwargs)


class TypeBinary(TypeExpr):
    left: TypeExpr
    operator: Optional[Token]
    right: TypeExpr

    def accept(self, visitor, **kwargs):
        return visitor.type_binary(self, **kwargs)


class TypeArray(TypeExpr):
    array: List[TypeExpr]

    def accept(self, visitor, **kwargs):
        return visitor.type_array(self, **kwargs)


class TypeMap(TypeExpr):
    map: Dict[str, TypeExpr]

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
        self._ip = ip
        self._definition = definition

    def __expr__(self):
        text = self.interpreter.printer.print(self.definition)
        return text

    def __str__(self):
        text = self.interpreter.printer.print(self.definition)
        return text

    @property
    def interpreter(self):
        return self._ip
    
    @property
    def definition(self):
        return self._definition


# Environment.

class Environment():

    def __init__(self, enclosing=None):
        self.enclosing: Optional['Environment'] = enclosing
        self.vars = {}

    def define(self, key: str, value: Value = None) -> bool:
        if value is None:
            value = Value(None, None)
        self.vars[key] = value
        return True

    def set(self, key: str, value: Value) -> bool:
        if key in self.vars:
            self.vars[key] = value
            return True
        if self.enclosing is not None:
            return self.enclosing.set(key, value)
        raise KeyError()

    def get(self, key: str) -> Value:
        if key in self.vars:
            return self.vars[key]
        if self.enclosing is not None:
            return self.enclosing.get(key)
        raise KeyError()


# Callables.


class FunctionObject():

    def __init__(self, ip: 'Interpreter', definition: Function): # type: ignore
        self._ip = ip
        self._definition = definition
        self._params = definition.parameters
        
        types = []

        # Create input types.
        if type(definition.types.left) == TypeArray:
            ptypes = definition.types.left.array
            assert(len(self.params) == len(ptypes))
            for ptype in ptypes:
                typedef = TypeDefinition(expr=ptype)
                usertype = Value(UserType(ip, typedef), None)
                types.append(usertype)
        else:
            assert(len(self.params) == 1)
            ptype = definition.types.left
            typedef = TypeDefinition(expr=ptype)
            usertype = Value(UserType(ip, typedef), None)
            types.append(usertype)

        # Create output type.
        ptype = definition.types.right
        typedef = TypeDefinition(expr=ptype)
        usertype = Value(UserType(ip, typedef), None)
        types.append(usertype)

        self._types = types

        # print(f"function initialization: types = {self.types}")

    @property
    def interpreter(self) -> 'Interpreter': # type: ignore
        return self._ip
    
    @property
    def params(self) -> List[str]:
        return self._params
    
    @property
    def types(self) -> List[Value]:
        return self._types
    
    @property
    def definition(self) -> Function:
        return self._definition

    @abstractmethod
    def call(self, args: List[Value]) -> Value:  # type: ignore
        pass

    def __repr__(self):
        # print(f"UserFunction.repr: definition = {self.definition}")
        return self.interpreter.printer.print(self.definition)

    def __str__(self):
        # print(f"UserFunction.str: definition = {self.definition}")
        return self.interpreter.printer.print(self.definition)


class NativeFunction(FunctionObject):

    def __init__(self, ip: 'Interpreter', definition: Union[Function,str]): # type: ignore
        if type(definition) == str:
            definition = ip.parser.parse(definition + " do null end").program[0]
        super().__init__(ip, definition)
        self._definition.expr = Terminal(
            token=Token(
                ttype=TokenType.TYPE,
                literal="<native function>"
            )
        )

    def call(self, args: List[Value]) -> Value:
        # Call function with new environment containing arguments.
        if len(self.params) != len(args):
            raise TypeError("Wrong number of parameters")
        # Call function with new environment containing arguments.
        env = Environment(enclosing=self.interpreter.env)
        for index in range(len(self.params)):
            if not self.interpreter.checktype(args[index], self.types[index]):
                raise TypeError(f"Wrong type of function argument.")
        value = self.func(args)
        if not self.interpreter.checktype(value, self.types[-1]):
            raise TypeError(f"Wrong type of function output.")
        return value

    @abstractmethod
    def func(self, args: List[Value]) -> Value:
        pass



class UserFunction(FunctionObject):

    def __init__(self, ip: 'Interpreter', definition: Function): # type: ignore
        super().__init__(ip, definition)

    def call(self, args: List[Value]) -> Value:
        if len(self.params) != len(args):
            raise TypeError("Wrong number of parameters")
        # Call function with new environment containing arguments.
        env = Environment(enclosing=self.interpreter.env)
        for index in range(len(self.params)):
            if not self.interpreter.checktype(args[index], self.types[index]):
                raise TypeError(f"Wrong type of function argument.")
            self.interpreter.define(self.params[index].literal, args[index])
        try:
            value = self.interpreter.execute_block(self.definition.expr, env)
        except Return as e:
            value = e.expr
        if not self.interpreter.checktype(value, self.types[-1]):
            raise TypeError(f"Wrong type of function output.")
        return value


