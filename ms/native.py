from typing import List, Any
from ms.ast import NativeFunction, Value, Environment
from ms.interpreter import Interpreter
from ms.types import TypeChecker

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


class Import(NativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "function(filename: Str) -> {}")
        self.ip = ip

    def func(self, args: List[Any]):
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
        return Value(module, None)


class Str(NativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "function(value: Any) -> Str")
        self.ip = ip

    def func(self, args: List[Any]):
        repr = self.ip.printer.print(args[0])
        return Value(repr, None)


class Print(NativeFunction):
    def __init__(self, ip: Interpreter):
        definition = "function(value: Any) -> Any"
        super().__init__(ip, definition)
        self.ip = ip

    def func(self, args: List[Value]):
        if type(args[0].value) == str:
            print(args[0].value)
        else:
            repr = self.ip.printer.print(args[0])
            print(repr)
        return args[0]


class Dump(NativeFunction):
    def __init__(self, ip: Interpreter):
        definition = "function() -> Null"
        super().__init__(ip, definition)
        self.ip = ip

    def func(self, args: List[Value]):
        if len(args) == 0:
            tag = ""
        else:
            tag = args[0]
        env = self.ip.env
        pre = "=> "
        print("=== STATE DUMP START")
        while env is not None:
            print(pre)
            txt = self.ip.printer.print(Value(env.vars, None))
            print(txt)
            pre = "==" + pre
            env = env.enclosing
        print("=== STATE DUMP END")
        return Value(None, None)


class GetEnv(NativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "function() -> {}")
        self.ip = ip

    def func(self, args: List[Any]):
        return Value(self.ip.env.vars, None)


class TypeOf(NativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "function(value: Any) -> Type")
        self.ip = ip

    def func(self, args: List[Any]):
        usertype = self.ip.typeof(args[0])
        return Value(usertype, None)


class IsSubtype(NativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "function(sub: Type, super: Type) -> Bool")
        self.ip = ip

    def func(self, args: List[Any]):
        valtype = self.ip.issubtype(args[0], args[1])
        return Value(valtype, None)


def interpreter(interactive=False):
    ip = Interpreter(interactive=interactive)
    ip.define("import", Value(Import(ip=ip)))
    ip.define("str", Value(Str(ip=ip)))
    ip.define("print", Value(Print(ip=ip)))
    ip.define("dump", Value(Dump(ip=ip)))
    ip.define("get_env", Value(GetEnv(ip=ip)))
    ip.define("typeof", Value(TypeOf(ip=ip)))
    ip.define("issubtype", Value(IsSubtype(ip=ip)))

    # Clean the lexer's code buffer.
    ip.parser.lexer.reset()
    return ip
