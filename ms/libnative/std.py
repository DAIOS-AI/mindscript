from typing import List, Any
from copy import deepcopy
from ms.objects import MNativeFunction, MValue, MObject
from ms.interpreter import Interpreter, Environment
from ms.types import TypeChecker
from ms.schema import JSONSchema
from ms.bnf import BNFFormatter
import ms.startup

# Native functions.


def flattened_env(env: Environment):
    fenv = dict()
    while env is not None:
        for key, val in env.vars.items():
            if key not in fenv:
                fenv[key] = val
        env = env.enclosing
    return fenv


class Import(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(filename: Str) -> Object")
        self.annotation = "Imports a module located at a given filename."

    def func(self, args: List[MObject]):
        filename = args[0].value
        try:
            with open(filename, "r") as fh:
                code = fh.read()

            ip = ms.startup.interpreter()
            startup_env = ip.env
            module_env = Environment(enclosing=startup_env)

            ip.env = module_env
            ip.eval(code)

            module_env.enclosing = None
            module = flattened_env(ip.env)
            module_env.enclosing = startup_env
        except FileNotFoundError as e:
            self.error(f"File not found: {filename}")
        except Exception as e:
            self.error(str(e))
        return MValue(module, None)


class Str(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(value: Any) -> Str")
        self.annotation = "Converts a value into a string."

    def func(self, args: List[MObject]):
        arg = args[0]
        repr = self.interpreter.print(arg)
        return MValue(repr, None)


class Bool(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(value: Any) -> Bool?")
        self.annotation = "Converts a value into a boolean."

    def func(self, args: List[MObject]):
        arg = args[0]
        try:
            if type(arg) == MValue:
                repr = bool(arg.value)
                return MValue(repr, None)
        except ValueError:
            pass
        return MValue(None, None)


class Int(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(value: Any) -> Int?")
        self.annotation = "Converts a value into an integer."

    def func(self, args: List[MObject]):
        arg = args[0]
        try:
            if type(arg) == MValue:
                repr = int(arg.value)
                return MValue(repr, None)
        except ValueError:
            pass
        return MValue(None, None)


class Num(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(value: Any) -> Num?")
        self.annotation = "Converts a value into a string."

    def func(self, args: List[MObject]):
        arg = args[0]
        try:
            if type(arg) == MValue:
                repr = float(arg.value)
                return MValue(repr, None)
        except ValueError:
            pass
        return MValue(None, None)


class Print(MNativeFunction):
    def __init__(self, ip: Interpreter):
        definition = "fun(value: Any) -> Any"
        super().__init__(ip, definition)
        self.annotation = "Prints a value."

    def func(self, args: List[MObject]):
        arg = args[0]
        if type(arg) == MValue and type(arg.value) == str:
            print(arg.value)
        else:
            repr = self.interpreter.print(arg)
            print(repr)
        return arg


class Exit(MNativeFunction):
    def __init__(self, ip: Interpreter):
        definition = "fun(_: Null) -> Null"
        super().__init__(ip, definition)
        self.annotation = "Exits the program."

    def func(self, args: List[MObject]):
        self.interpreter.exit()


class Dump(MNativeFunction):
    def __init__(self, ip: Interpreter):
        definition = "fun() -> Null"
        super().__init__(ip, definition)
        self.annotation = "Prints the current environment and its parents."

    def func(self, args: List[MObject]):
        env = self.interpreter.env
        pre = "=> "
        print("=== STATE DUMP START")
        while env is not None:
            print(pre)
            txt = self.interpreter.print(MValue(env.vars, None))
            print(txt)
            pre = "==" + pre
            env = env.enclosing
        print("=== STATE DUMP END")
        return MValue(None, None)


class GetEnv(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun() -> Object")
        self.annotation = "Returns the current environment."

    def func(self, args: List[MObject]):
        env = flattened_env(self.interpreter.env)
        return MValue(env, None)


class Assert(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(condition: Bool) -> Bool")
        self.annotation = "Asserts the condition."

    def func(self, args: List[MObject]):
        arg = args[0]
        if not arg.value:
            self.error("Assertion failed.")
        return MValue(True, None)


class Error(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(message: Str?) -> Null")
        self.annotation = "Throws a runtime error."

    def func(self, args: List[MObject]):
        arg = args[0]
        if arg.value is None:
            self.error("")
        else:
            self.error(arg.value)
        return MValue(None, None)


class TypeOf(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(value: Any) -> Type")
        self.annotation = "Returns the type of the value."

    def func(self, args: List[MObject]):
        arg = args[0]
        return self.interpreter.typeof(arg)


class IsType(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(value: Any, ttype: Type) -> Bool")
        self.annotation = "Checks whether a value conforms to a given type."

    def func(self, args: List[MObject]):
        val, ttype = args
        try:
            confirmed = self.interpreter.checktype(val, ttype)
        except Exception as e:
            self.error(str(e))
        return MValue(confirmed, None)


class IsSubtype(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(subtype: Type, supertype: Type) -> Bool")
        self.annotation = "Checks whether a type is a subtype of another type."

    def func(self, args: List[MObject]):
        try:
            confirmed = self.interpreter.issubtype(args[0], args[1])
        except Exception as e:
            self.error(str(e))
        return MValue(confirmed, None)


class Schema(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(value: Type) -> Str")
        self.annotation = "Returns the JSON schema of a type."
        self.printer = JSONSchema(ip)

    def func(self, args: List[MObject]):
        arg = args[0]
        try:
            valtype = self.printer.print_schema(arg)
        except Exception as e:
            self.error(str(e))
        return MValue(valtype, None)


class BNF(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(value: Type) -> Str")
        self.annotation = "Returns the BNF grammar of a type."
        self.formatter = BNFFormatter(ip)

    def func(self, args: List[MObject]):
        arg = args[0]
        try:
            valtype = self.formatter.format(arg)
        except Exception as e:
            self.error(str(e))
        return MValue(valtype, None)


class Size(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(value: Any) -> Int?")
        self.annotation = "Returns the size of a collection or a string."

    def func(self, args: List[MObject]):
        arg = args[0]
        if type(arg) != MValue or type(arg.value) not in [list, dict, str]:
            return MValue(None, None)
        return MValue(len(arg.value), None)


class Clone(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(value: Any) -> Any")
        self.annotation = "Makes a deep clone of a value."

    def func(self, args: List[MObject]):
        arg = args[0]
        return deepcopy(arg)


class BindFun(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(value: Any, func: Any -> Any) -> Any -> Any")
        self.annotation = "Binds a function to a value."

    def func(self, args: List[MObject]):
        obj, fun = args
        fun._env.define("this", obj)
        return fun


class UniqueId(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(value: Any) -> Int")
        self.annotation = "Returns the unique value identifier."

    def func(self, args: List[MObject]):
        value = args[0]
        return MValue(id(value), None)


class SetAnnotation(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(value: Any, annotation: Str?) -> Any")
        self.annotation = "Annotates a value."

    def func(self, args: List[MObject]):
        value, note = args
        value.annotation = note.value
        return value


class GetAnnotation(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(value: Any) -> Str?")
        self.annotation = "Get a value's annotation."

    def func(self, args: List[MObject]):
        value = args[0]
        return MValue(value.annotation, None)
