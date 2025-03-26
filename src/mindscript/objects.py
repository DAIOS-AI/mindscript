from typing import Optional, List, Union, Any
from abc import abstractmethod
import mindscript.ast as ast
from copy import deepcopy
from functools import partialmethod

# Value types

# Primitive value.


class MObject():
    @property
    @abstractmethod
    def annotation(self):
        pass


class MValue(MObject):
    def __init__(self, value, annotation=None):
        self._value = value
        self._annotation = annotation

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        self._value = val

    @property
    def annotation(self):
        return self._annotation

    @annotation.setter
    def annotation(self, val):
        self._annotation = val


def wrap(val: Any):
    if type(val) in [type(None), bool, int, float, str]:
        return MValue(val, None)
    elif type(val) == list:
        mval = []
        for subval in val:
            mval.append(wrap(subval))
        return MValue(mval)
    elif type(val) == dict:
        mval = {}
        for key, subval in val.items():
            mval[key] = wrap(subval)
        return MValue(mval)
    raise ValueError(f"Cannot wrap a value of type {type(val)}.")


def unwrap(mval: MValue, ignore: bool = True):
    if type(mval) != MValue:
        raise ValueError(f"Cannot unwrap a value of type {type(mval)}")
    elif type(mval.value) in [type(None), bool, int, float, str]:
        return mval.value
    elif type(mval.value) == list:
        val = []
        for subval in mval.value:
            val.append(unwrap(subval))
        return val
    elif type(mval.value) == dict:
        val = {}
        for key, subval in mval.value.items():
            val[key] = unwrap(subval)
        return val
    elif ignore:
        return None
    raise ValueError(f"Cannot unwrap a value of type {type(mval.value)}")


# Types.


class MType(MObject):

    def __init__(self, ip: 'Interpreter', definition: ast.TypeExpr):  # type: ignore
        self._ip = ip
        self._env = ip.env
        self._definition = definition

    @property
    def interpreter(self):
        return self._ip

    @property
    def environment(self):
        return self._env

    @property
    def definition(self):
        return self._definition

    @property
    def annotation(self):
        self._definition.annotation

    @annotation.setter
    def annotation(self, note):
        self._definition.annotation = note


# Callables.

class MFunction(MObject):

    def __init__(self, ip: 'Interpreter', definition: ast.Function):  # type: ignore
        self._ip = ip
        self._env = ip.env
        self._definition = definition
        self._operator = definition.operator

        # Create input  types.
        self._intypes = []
        types = definition.types
        while len(self._intypes) < len(definition.parameters):
            ptype = types.left
            typeobj = MType(ip, ptype)
            self._intypes.append(typeobj)
            types = types.right
        ptype = types
        typeobj = MType(ip, ptype)
        self._outtype = typeobj

    @property
    def interpreter(self) -> 'Interpreter':  # type: ignore
        return self._ip

    @property
    def environment(self) -> 'Environment':  # type: ignore
        return self._env

    @property
    def params(self) -> List[str]:
        return self._definition.parameters

    @property
    def intypes(self) -> List[MObject]:
        return self._intypes

    @property
    def outtype(self) -> MObject:
        return self._outtype

    @property
    def definition(self) -> ast.Function:
        return self._definition

    @property
    def annotation(self):
        return self._definition.types.annotation

    @annotation.setter
    def annotation(self, note):
        self._definition.types.annotation = note

    def call(self, operator: ast.Token, args: List[MObject]) -> MObject:
        self._operator = operator

        if len(args) < len(self.params):
            return self.partial(args)
        for arg, typeobj in zip(args, self.intypes):
            if not self.interpreter.checktype(arg, typeobj):
                reqtype_str = self.interpreter.printer.print(typeobj)
                val_str = self.interpreter.printer.print(arg)
                valtype_str = self.interpreter.printer.print(
                    self.interpreter.typeof(arg))
                self.error(f"Wrong type of function argument: "
                           f"Expected {reqtype_str} but got value {val_str} of {valtype_str}.")

        value = self.func(args)

        if not self.interpreter.checktype(value, self.outtype):
            reqtype_str = self.interpreter.printer.print(self.outtype)
            val_str = self.interpreter.printer.print(value)
            valtype_str = self.interpreter.printer.print(
                self.interpreter.typeof(value))
            self.error(f"Wrong type of function output: "
                       f"Expected {reqtype_str} but got value {val_str} of {valtype_str}.")

        return value

    def partial(self, args: List[MObject]) -> MObject:
        n_args = len(args)
        funcobj = deepcopy(self)
        funcobj.func = lambda new_args: self.func(args + new_args)
        funcobj._definition.parameters = funcobj.params[n_args:]
        funcobj._intypes = funcobj._intypes[n_args:]
        types = funcobj.definition.types.right
        for _ in range(len(args)-1):
            types = types.right
        funcobj._definition.types = types
        return funcobj

    def error(self, msg: str):
        self.interpreter.error(self._operator, msg)

    @abstractmethod
    def func(self, args: List[MObject]) -> MObject:
        pass

    def __repr__(self):
        # print(f"UserFunction.repr: definition = {self.definition}")
        return "<function>"

    def __str__(self):
        # print(f"UserFunction.str: definition = {self.definition}")
        return "<function>"


class MPartialFunction(MFunction):

    def __init__(self, ip: 'Interpreter', definition: Union[ast.Function, str]): # type: ignore
        if type(definition) == str:
            buffer = ip.get_buffer()
            definition = ip.parser.parse(
                definition + " do null end\n", "<native def>").program[0]
            ip.set_buffer(buffer)
        super().__init__(ip, definition)

    @abstractmethod
    def func(self, args: List[MObject]) -> MObject:
        pass


class MNativeFunction(MFunction):

    def __init__(self, ip: 'Interpreter', definition: Union[ast.Function, str]): # type: ignore
        if type(definition) == str:
            buffer = ip.buffer
            definition = ip.parser.parse(
                definition + " do null end\n", "<native def>").program[0]
            ip.set_buffer(buffer)
        super().__init__(ip, definition)

    @abstractmethod
    def func(self, args: List[MObject]) -> MObject:
        pass

    def __repr__(self):
        return "<native function>"

    def __str__(self):
        return "<native function>"
