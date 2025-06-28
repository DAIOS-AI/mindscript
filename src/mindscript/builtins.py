from importlib.resources import files

import mindscript.libnative.std as std
import mindscript.libnative.collections as collections
import mindscript.libnative.math as math
import mindscript.libnative.string as string
import mindscript.libnative.network as network
import mindscript.libnative.system as system
from mindscript.runtime import Interpreter


def read_lib_script(filename: str):
    return files('mindscript.lib').joinpath(filename).read_text()


def interpreter(interactive=False, backend = None):
    ip = Interpreter(interactive=interactive, backend=backend)

    ip.set_buffer("<core>")

    # Register built-in native symbols.
    ip.define("codeImport", std.CodeImport(ip=ip))
    ip.define("import", std.Import(ip=ip))
    ip.define("str", std.Str(ip=ip))
    ip.define("bool", std.Bool(ip=ip))
    ip.define("int", std.Int(ip=ip))
    ip.define("num", std.Num(ip=ip))
    ip.define("print", std.Print(ip=ip))
    ip.define("println", std.Println(ip=ip))
    ip.define("dump", std.Dump(ip=ip))
    ip.define("getEnv", std.GetEnv(ip=ip))
    ip.define("typeOf", std.TypeOf(ip=ip))
    ip.define("isType", std.IsType(ip=ip))
    ip.define("isSubtype", std.IsSubtype(ip=ip))
    ip.define("schema", std.Schema(ip=ip))
    ip.define("assert", std.Assert(ip=ip))
    ip.define("bnf", std.BNF(ip=ip))
    ip.define("error", std.Error(ip=ip))
    ip.define("exit", std.Exit(ip=ip))
    ip.define("size", std.Size(ip=ip))
    ip.define("clone", std.Clone(ip=ip))
    ip.define("bindMethod", std.BindMethod(ip=ip))
    ip.define("uid", std.UniqueId(ip=ip))
    ip.define("setNote", std.SetNote(ip=ip))
    ip.define("getNote", std.GetNote(ip=ip))

    ip.define("PI", math.PI)
    ip.define("E", math.E)
    ip.define("sin", math.Sin(ip=ip))
    ip.define("cos", math.Cos(ip=ip))
    ip.define("tan", math.Tan(ip=ip))
    ip.define("sqrt", math.Sqrt(ip=ip))
    ip.define("log", math.Log(ip=ip))
    ip.define("exp", math.Exp(ip=ip))
    ip.define("pow", math.Pow(ip=ip))

    ip.define("substr", string.SubStr(ip=ip))
    ip.define("toLower", string.ToLower(ip=ip))
    ip.define("toUpper", string.ToUpper(ip=ip))
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
    ip.define("get", collections.Get(ip=ip))
    ip.define("set", collections.Set(ip=ip))

    ip.eval(network.HTTPParams)
    ip.define("http", network.HTTP(ip=ip))

    ip.define("tsNow", system.TsNow(ip=ip))
    ip.define("dateNow", system.DateNow(ip=ip))
    ip.define("random", system.Random(ip=ip))

    # Register built-in symbols.
    code = read_lib_script("std.ms")
    ip.eval(code, "<prelude>")

    # Clean the lexer's code buffer (disabled now).
    # ip.parser.lexer.reset()

    # Now mark the current environment as part of the startup.
    ip.mark_startup_environment()

    return ip
