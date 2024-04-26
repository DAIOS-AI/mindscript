from typing import List, Any
from ms.objects import MNativeFunction, MValue, MObject, Environment
from ms.interpreter import Interpreter
from ms.types import TypeChecker
from ms.schema import JSONSchema

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
        super().__init__(ip, "function(filename: Str) -> {}")
        self.ip = ip

    def func(self, args: List[MObject]):
        try:
            with open(args[0].value, "r") as fh:
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
            print(f"File not found: {args[0]}")
            return None
        except Exception as e:
            print(e)
            return None
        return MValue(module, None)


class Str(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "function(value: Any) -> Str")
        self.ip = ip

    def func(self, args: List[MObject]):
        repr = self.ip.printer.print(args[0])
        return MValue(repr, None)


class Print(MNativeFunction):
    def __init__(self, ip: Interpreter):
        definition = "function(value: Any) -> Any"
        super().__init__(ip, definition)
        self.ip = ip

    def func(self, args: List[MObject]):
        if type(args[0].value) == str:
            print(args[0].value)
        else:
            repr = self.ip.printer.print(args[0])
            print(repr)
        return args[0]


class Dump(MNativeFunction):
    def __init__(self, ip: Interpreter):
        definition = "function() -> Null"
        super().__init__(ip, definition)
        self.ip = ip

    def func(self, args: List[MObject]):
        if len(args) == 0:
            tag = ""
        else:
            tag = args[0]
        env = self.ip.env
        pre = "=> "
        print("=== STATE DUMP START")
        while env is not None:
            print(pre)
            txt = self.ip.printer.print(MValue(env.vars, None))
            print(txt)
            pre = "==" + pre
            env = env.enclosing
        print("=== STATE DUMP END")
        return MValue(None, None)


class GetEnv(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "function() -> {}")
        self.ip = ip

    def func(self, args: List[MObject]):
        return MValue(self.ip.env.vars, None)


class TypeOf(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "function(value: Any) -> Type")
        self.ip = ip

    def func(self, args: List[Any]):
        return self.ip.typeof(args[0])


class IsSubtype(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "function(sub: Type, super: Type) -> Bool")
        self.ip = ip

    def func(self, args: List[Any]):
        confirmed = self.ip.issubtype(args[0], args[1])
        return MValue(confirmed, None)

class Schema(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "function(value: Type) -> Str")
        self.ip = ip
        self.printer = JSONSchema()

    def func(self, args: List[Any]):
        valtype = self.printer.print_schema(args[0])
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

    # Clean the lexer's code buffer.
    ip.parser.lexer.reset()
    return ip
