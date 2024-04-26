from typing import Optional, List, Union
from abc import abstractmethod
import ms.ast as ast

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



# Environment.

class Environment():

    def __init__(self, enclosing=None):
        self.enclosing: Optional['Environment'] = enclosing
        self.vars = {}

    def define(self, key: str, value: MValue = None) -> bool:
        if value is None:
            value = MValue(None, None)
        self.vars[key] = value
        return True

    def set(self, key: str, value: MValue) -> bool:
        if key in self.vars:
            self.vars[key] = value
            return True
        if self.enclosing is not None:
            return self.enclosing.set(key, value)
        raise KeyError()

    def get(self, key: str) -> MObject:
        if key in self.vars:
            return self.vars[key]
        if self.enclosing is not None:
            return self.enclosing.get(key)
        raise KeyError()



# Types.


class MType(MObject):

    def __init__(self, ip: 'Interpreter', definition: ast.TypeExpr):  # type: ignore
        self._ip = ip
        self._env = ip.env
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
        self._params = definition.parameters

        types = []

        # Create input types.
        if type(definition.types.left) == ast.TypeArray:
            ptypes = definition.types.left.array
            assert (len(self.params) == len(ptypes))
            for ptype in ptypes:
                usertype = MType(ip, ptype)
                types.append(usertype)
        else:
            assert (len(self.params) == 1)
            ptype = definition.types.left
            usertype = MType(ip, ptype)
            types.append(usertype)

        # Create output type.
        ptype = definition.types.right
        usertype = MType(ip, ptype)
        types.append(usertype)

        self._types = types

        # print(f"function initialization: types = {self.types}")

    @property
    def interpreter(self) -> 'Interpreter':  # type: ignore
        return self._ip

    @property
    def environment(self) -> 'Environment':  # type: ignore
        return self._env

    @property
    def params(self) -> List[str]:
        return self._params

    @property
    def types(self) -> List[MObject]:
        return self._types

    @property
    def definition(self) -> ast.Function:
        return self._definition

    @property
    def annotation(self):
        return self._definition.types.annotation
    
    @annotation.setter
    def annotation(self, note):
        self._definition.types.annotation = note

    @abstractmethod
    def call(self, args: List[MObject]) -> MObject:  # type: ignore
        pass

    def __repr__(self):
        # print(f"UserFunction.repr: definition = {self.definition}")
        return self.interpreter.printer.print(self.definition)

    def __str__(self):
        # print(f"UserFunction.str: definition = {self.definition}")
        return self.interpreter.printer.print(self.definition)


class MNativeFunction(MFunction):

    # type: ignore
    def __init__(self, ip: 'Interpreter', definition: Union[ast.Function, str]): # type: ignore
        if type(definition) == str:
            definition = ip.parser.parse(
                definition + " do null end").program[0]
        super().__init__(ip, definition)
        self._definition.expr = ast.Terminal(
            token=ast.Token(
                ttype=ast.TokenType.TYPE,
                literal="<native function>"
            )
        )

    def call(self, args: List[MObject]) -> MObject:
        # Call function with new environment containing arguments.
        if len(self.params) != len(args):
            raise ast.TypeError("Wrong number of parameters")
        # Call function with new environment containing arguments.
        env = Environment(enclosing=self.environment)
        for index in range(len(self.params)):
            if not self.interpreter.checktype(args[index], self.types[index]):
                raise ast.TypeError(f"Wrong type of function argument.")
        value = self.func(args)
        if not self.interpreter.checktype(value, self.types[-1]):
            raise ast.TypeError(f"Wrong type of function output.")
        return value

    @abstractmethod
    def func(self, args: List[MObject]) -> MObject:
        pass


class MUserFunction(MFunction):

    def __init__(self, ip: 'Interpreter', definition: ast.Function):  # type: ignore
        super().__init__(ip, definition)

    def call(self, args: List[MObject]) -> MObject:
        if len(self.params) != len(args):
            raise ast.TypeError("Wrong number of parameters")
        # Call function with new environment containing arguments.
        env = Environment(enclosing=self.environment)
        for index in range(len(self.params)):
            if not self.interpreter.checktype(args[index], self.types[index]):
                raise ast.TypeError(f"Wrong type of function argument.")
            self.interpreter.define(self.params[index].literal, args[index])
        try:
            value = self.interpreter.execute_block(self.definition.expr, env)
        except ast.Return as e:
            value = e.expr
        if not self.interpreter.checktype(value, self.types[-1]):
            raise ast.TypeError(f"Wrong type of function output.")
        return value


