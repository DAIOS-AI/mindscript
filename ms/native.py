from typing import List, Any
from ms.objects import MNativeFunction, MValue, MObject
from ms.interpreter import Interpreter, Environment
from ms.types import TypeChecker
from ms.schema import JSONSchema
from ms.bnf import BNFFormatter


# Native functions.

# class IsType(NativeFunction):
#     def __init__(self, ip: Interpreter):
#         super(IsType, self).__init__(ip)
#         self.ip = ip
#         self.checker = ValueAsType()

#     def call(self, args: List[Any]):
#         data = args[0]
#         typedata = args[1]
#         return self.checker.check(typedata, data)


class Import(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(filename: Str) -> Object")

    def func(self, args: List[MObject]):
        filename = args[0].value
        try:
            with open(filename, "r") as fh:
                code = fh.read()

            ip = interpreter()
            ip.env = Environment(enclosing=ip.env)
            ip.eval(code)
            module = dict()
            env = ip.env
            while env is not None:
                for key, val in env.vars.items():
                    if key not in module:
                        module[key] = val
                env = env.enclosing
        except FileNotFoundError as e:
            self.error(f"File not found: {filename}")
        except Exception as e:
            self.error(str(e))
        return MValue(module, None)


class Str(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(value: Any) -> Str")

    def func(self, args: List[MObject]):
        arg = args[0]
        repr = self.interpreter.print(arg)
        return MValue(repr, None)


class Print(MNativeFunction):
    def __init__(self, ip: Interpreter):
        definition = "fun(value: Any) -> Any"
        super().__init__(ip, definition)

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

    def func(self, args: List[MObject]):
        self.interpreter.exit()



class Dump(MNativeFunction):
    def __init__(self, ip: Interpreter):
        definition = "fun() -> Null"
        super().__init__(ip, definition)

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

    def func(self, args: List[MObject]):
        return MValue(self.interpreter.env.vars, None)


class TypeOf(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(value: Any) -> Type")

    def func(self, args: List[MObject]):
        arg = args[0]
        return self.interpreter.typeof(arg)


class Assert(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(value: Bool) -> Bool")

    def func(self, args: List[MObject]):
        arg = args[0]
        if not arg.value:
            self.error("Assertion failed.")
        return MValue(True, None)


class Error(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(message: Str?) -> Null")
    
    def func(self, args: List[MObject]):
        arg = args[0]
        if arg.value is None:
            self.error("")
        else:
            self.error(arg.value)
        return MValue(None, None)


class IsSubtype(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(subtype: Type, supertype: Type) -> Bool")

    def func(self, args: List[MObject]):
        try:
            confirmed = self.interpreter.issubtype(args[0], args[1])
        except Exception as e:
            self.error(str(e))
        return MValue(confirmed, None)


class Schema(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(value: Type) -> Str")
        self.printer = JSONSchema()

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
        self.formatter = BNFFormatter()

    def func(self, args: List[MObject]):
        arg = args[0]
        try:
            valtype = self.formatter.format(arg)
        except Exception as e:
            self.error(str(e))
        return MValue(valtype, None)


def interpreter(interactive=False):
    ip = Interpreter(interactive=interactive)
    ip.define("import", Import(ip=ip))
    ip.define("str", Str(ip=ip))
    ip.define("print", Print(ip=ip))
    ip.define("dump", Dump(ip=ip))
    ip.define("get_env", GetEnv(ip=ip))
    ip.define("typeof", TypeOf(ip=ip))
    ip.define("issubtype", IsSubtype(ip=ip))
    ip.define("schema", Schema(ip=ip))
    ip.define("assert", Assert(ip=ip))
    ip.define("bnf", BNF(ip=ip))
    ip.define("error", Error(ip=ip))
    ip.define("exit", Exit(ip=ip))

    # Clean the lexer's code buffer.
    ip.parser.lexer.reset()
    return ip
