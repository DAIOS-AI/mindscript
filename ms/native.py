from typing import List, Any
from ms.ast import NativeCallable, Value
from ms.interpreter import Interpreter, Environment


# Native functions.

class Import(NativeCallable):
    def __init__(self, ip: Interpreter):
        super(Import, self).__init__(ip)
        self.ip = ip
    
    def call(self, args: List[Any]):
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

class Str(NativeCallable):
    def __init__(self, ip: Interpreter):
        super(Str, self).__init__(ip)
        self.ip = ip
    
    def call(self, args: List[Any]):
        repr = self.ip.printer.print(args[0])
        return repr

class Print(NativeCallable):
    def __init__(self, ip: Interpreter):
        super(Print, self).__init__(ip)
        self.ip = ip

    def call(self, args: List[Any]):
        repr = self.ip.printer.print(args[0])
        print(repr)
        return args[0]

class Dump(NativeCallable):
    def __init__(self, ip: Interpreter):
        super(Dump, self).__init__(ip)
        self.ip = ip

    def call(self, args: List[Any]):
        if len(args) == 0:
            tag = ""
        else:
            tag = args[0]
        env = self.ip.env
        pre = "=> "
        print("=== STATE DUMP START")
        while env is not None:
            print(pre)
            txt = self.ip.printer.print(env.vars)
            print(txt)
            pre = "==" + pre
            env = env.enclosing
        print("=== STATE DUMP END")
        return None

class GetEnv(NativeCallable):
    def __init__(self, ip: Interpreter):
        super(GetEnv, self).__init__(ip)
        self.ip = ip

    def call(self, args: List[Any]):
        return self.ip.env.vars


def interpreter(interactive=False):
    ip = Interpreter(interactive=interactive)
    ip.define("import", Value(Import(ip=ip)))
    ip.define("str", Value(Str(ip=ip)))
    ip.define("print", Value(Print(ip=ip)))
    ip.define("dump", Value(Dump(ip=ip)))
    ip.define("get_env", Value(GetEnv(ip=ip)))
    return ip
