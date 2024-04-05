from typing import List, Any
from scripting.interpreter import Interpreter, Callable, NativeCallable, UserCallable, UserType


# Native functions.

class Print(NativeCallable):
    def __init__(self, ip: Interpreter):
        self.ip = ip

    def call(self, args: List[Any]):
        arg = args[0]
        item = ""
        if arg is None:
            item = "null"
        elif isinstance(arg, bool):
            item = "true" if arg else "false"
        elif isinstance(arg, UserCallable):
            item = self.ip.printer.print(arg.function)
        elif isinstance(arg, UserType):
            item = self.ip.printer.print(arg.definition)
        else:
            item = str(arg)
        print(item)
        return arg


class Dump(NativeCallable):
    def __init__(self, ip: Interpreter):
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
        self.ip = ip

    def call(self, args: List[Any]):
        return self.ip.env.vars


def interpreter(interactive=False):
    ip = Interpreter(interactive=interactive)
    ip.define("print", Print(ip=ip))
    ip.define("dump", Dump(ip=ip))
    ip.define("get_env", GetEnv(ip=ip))
    return ip
