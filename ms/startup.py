import ms.native.std as std
import ms.native.collections as collections
import ms.native.math as math
import ms.native.string as string
import ms.native.network as network
import ms.native.system as system
from ms.interpreter import Interpreter

def interpreter(interactive=False):
    ip = Interpreter(interactive=interactive)

    # Register built-in native symbols.
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
    ip.define("clone", std.Clone(ip=ip))
    ip.define("bindFun", std.BindFun(ip=ip))
    ip.define("uid", std.UniqueId(ip=ip))
    ip.define("annotate", std.Annotate(ip=ip))

    ip.define("PI", math.PI)
    ip.define("E", math.E)
    ip.define("sin", math.Sin(ip=ip))
    ip.define("cos", math.Cos(ip=ip))
    ip.define("tan", math.Tan(ip=ip))
    ip.define("sqrt", math.Sqrt(ip=ip))
    ip.define("log", math.Log(ip=ip))
    ip.define("pow", math.Pow(ip=ip))

    ip.define("substr", string.SubStr(ip=ip))
    ip.define("tolower", string.ToLower(ip=ip))
    ip.define("toupper", string.ToUpper(ip=ip))
    ip.define("strip", string.Strip(ip=ip))
    ip.define("lstrip", string.LStrip(ip=ip))
    ip.define("rstrip", string.RStrip(ip=ip))
    ip.define("split", string.Split(ip=ip))
    ip.define("join", string.Join(ip=ip))
    ip.define("match", string.Match(ip=ip))
    ip.define("replace", string.Replace(ip=ip))

    ip.define("iter", collections.Iter(ip=ip))
    ip.define("slice", collections.Slice(ip=ip))
    ip.define("push", collections.Push(ip=ip))
    ip.define("pop", collections.Pop(ip=ip))
    ip.define("shift", collections.Shift(ip=ip))
    ip.define("unshift", collections.Unshift(ip=ip))
    ip.define("delete", collections.Delete(ip=ip))
    ip.define("keys", collections.Keys(ip=ip))
    ip.define("values", collections.Values(ip=ip))
    ip.define("exists", collections.Exists(ip=ip))

    ip.eval(network.HTTPParams)
    ip.define("http", network.HTTP(ip=ip))

    ip.define("tsNow", system.TsNow(ip=ip))
    ip.define("dateNow", system.DateNow(ip=ip))
    ip.define("random", system.Random(ip=ip))

    # Register built-in symbols.
    with open("ms/lib/std.ms") as fh:
        code = fh.read()
        ip.eval(code)

    # Clean the lexer's code buffer (disabled now).
    # ip.parser.lexer.reset()

    return ip
