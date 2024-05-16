from typing import List
from ms.objects import MNativeFunction, MValue, MObject
from ms.interpreter import Interpreter
import re
import math

# Arrays/Lists: push, pop, shift, unshift, map, filter, reduce, find
# Dictionaries/Hashes: put, get, remove, keys, values
# Sets: add, remove, union, intersection


class Slice(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(array: Array, s: Int, e: Int) -> Array")
        self.annotation = "Slices an array between two indexes."

    def func(self, args: List[MObject]):
        arr, s, e = args
        return MValue(arr.value[s.value: e.value], None)


class Push(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(array: Array, value: Any) -> Array")
        self.annotation = "Adds a value to the end of an array."

    def func(self, args: List[MObject]):
        arr, value = args
        arr.value.append(value)
        return arr


class Pop(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(array: Array) -> Any")
        self.annotation = "Pops the last value from the array."

    def func(self, args: List[MObject]):
        arr = args[0]
        return arr.value.pop(-1)


class Shift(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(array: Array, value: Any) -> Array")
        self.annotation = "Inserts a value at the front of an array."

    def func(self, args: List[MObject]):
        arr, value = args
        arr.value.insert(0, value)
        return arr


class Unshift(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(array: Array) -> Any")
        self.annotation = "Pops the first value from the array."

    def func(self, args: List[MObject]):
        arr = args[0]
        return arr.value.pop(0)


class Map(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(string: Str) -> Str")
        self.annotation = "Converts a string to uppercase."

    def func(self, args: List[MObject]):
        arg = args[0]
        return MValue(arg.value.upper(), None)


class Reduce(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(string: Str) -> Str")
        self.annotation = "Converts a string to uppercase."

    def func(self, args: List[MObject]):
        arg = args[0]
        return MValue(arg.value.upper(), None)


class Find(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(string: Str) -> Str")
        self.annotation = "Converts a string to uppercase."

    def func(self, args: List[MObject]):
        arg = args[0]
        return MValue(arg.value.upper(), None)


class Define(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(string: Str) -> Str")
        self.annotation = "Converts a string to uppercase."

    def func(self, args: List[MObject]):
        arg = args[0]
        return MValue(arg.value.upper(), None)


class Delete(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(string: Str) -> Str")
        self.annotation = "Converts a string to uppercase."

    def func(self, args: List[MObject]):
        arg = args[0]
        return MValue(arg.value.upper(), None)


class Keys(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(string: Str) -> Str")
        self.annotation = "Converts a string to uppercase."

    def func(self, args: List[MObject]):
        arg = args[0]
        return MValue(arg.value.upper(), None)


class Values(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(string: Str) -> Str")
        self.annotation = "Converts a string to uppercase."

    def func(self, args: List[MObject]):
        arg = args[0]
        return MValue(arg.value.upper(), None)
