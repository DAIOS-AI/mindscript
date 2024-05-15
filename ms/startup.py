import ms.native.std as std
import ms.native.array as array
from ms.interpreter import Interpreter

def interpreter(interactive=False):
    ip = Interpreter(interactive=interactive)

    # Register native functions.
    ip.define("import", std.Import(ip=ip))
    ip.define("str", std.Str(ip=ip))
    ip.define("print", std.Print(ip=ip))
    ip.define("dump", std.Dump(ip=ip))
    ip.define("getEnv", std.GetEnv(ip=ip))
    ip.define("typeof", std.TypeOf(ip=ip))
    ip.define("issubtype", std.IsSubtype(ip=ip))
    ip.define("schema", std.Schema(ip=ip))
    ip.define("assert", std.Assert(ip=ip))
    ip.define("bnf", std.BNF(ip=ip))
    ip.define("error", std.Error(ip=ip))
    ip.define("exit", std.Exit(ip=ip))
    ip.define("size", std.Size(ip=ip))

    # Clean the lexer's code buffer.
    ip.parser.lexer.reset()
    return ip
