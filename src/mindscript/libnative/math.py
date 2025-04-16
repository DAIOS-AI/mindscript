from typing import List
from mindscript.objects import MNativeFunction, MValue, MObject
from mindscript.runtime import Interpreter
import math

# Basic arithmetic operations: add, subtract, multiply, divide
# Advanced math functions: sin, cos, tan, log, sqrt, pow
# Constants: PI, E

PI = MValue(3.14159265359, "\u03C0")
E = MValue(2.7182818284, "Euler's number")


class Sin(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(value: Num) -> Num")
        self.annotation = "Sine function"

    def func(self, args: List[MObject]):
        arg = args[0]
        return MValue(math.sin(arg.value), None)


class Cos(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(value: Num) -> Num")
        self.annotation = "Cosine function"

    def func(self, args: List[MObject]):
        arg = args[0]
        return MValue(math.cos(arg.value), None)


class Tan(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(value: Num) -> Num")
        self.annotation = "Tangent function"

    def func(self, args: List[MObject]):
        arg = args[0]
        return MValue(math.tan(arg.value), None)


class Log(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(value: Num) -> Num?")
        self.annotation = "Logarithm function"

    def func(self, args: List[MObject]):
        arg = args[0]
        if arg.value <= 0.0:
            return MValue(None, None)
        return MValue(math.log(arg.value), None)


class Exp(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(value: Num) -> Num?")
        self.annotation = "Exponential function"

    def func(self, args: List[MObject]):
        arg = args[0]
        if arg.value <= 0.0:
            return MValue(None, None)
        return MValue(math.exp(arg.value), None)


class Sqrt(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(value: Num) -> Num")
        self.annotation = "Square-root function"

    def func(self, args: List[MObject]):
        arg = args[0]
        return MValue(math.sqrt(arg.value), None)


class Pow(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(base: Num, exp: Num) -> Num")
        self.annotation = "Power function"

    def func(self, args: List[MObject]):
        base, exp = args[0], args[1]
        return MValue(math.pow(base.value, exp.value), None)
