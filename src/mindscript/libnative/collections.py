from typing import List
from mindscript.objects import MNativeFunction, MValue, MObject
from mindscript.runtime import Interpreter
import re
import math

# Arrays/Objects: iter
# Arrays: slice, push, pop, shift, unshift, map, filter, reduce, find
# Objects: delete, keys, values
# Sets: add, remove, union, intersection


class Iter(MNativeFunction):

    class ArrayIterator(MNativeFunction):
        def __init__(self, ip: Interpreter, array: list):
            super().__init__(ip, "fun(_: Null) -> Any?")
            self.annotation = "An array iterator."
            self.array = array
            self.index = 0

        def func(self, args: List[MObject]):
            index = self.index
            if index < len(self.array):
                self.index += 1
                return self.array[index]
            return MValue(None, None)

    class ObjectIterator(MNativeFunction):
        def __init__(self, ip: Interpreter, obj: dict):
            super().__init__(ip, "fun(_: Null) -> Any?")
            self.annotation = "An object iterator."
            self.array = []
            for key, value in obj.items():
                keyval = MValue(key, None)
                pair = [keyval, value]
                self.array.append(pair)
            self.index = 0

        def func(self, args: List[MObject]):
            index = self.index
            if index < len(self.array):
                self.index += 1
                return MValue(self.array[index])
            return MValue(None, None)

    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(value: Any) -> Any")
        self.annotation = "Creates an iterator function from the value."

    def func(self, args: List[MObject]):
        arg = args[0]
        if type(arg) != MValue:
            return MValue(None, None)

        value = arg.value
        if type(value) == list:
            return Iter.ArrayIterator(self.interpreter, value)
        elif type(value) == dict:
            return Iter.ObjectIterator(self.interpreter, value)
        return MValue(None, None)


class Slice(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(array: [Any], s: Int, e: Int) -> [Any]")
        self.annotation = "Slices an array between two indexes."

    def func(self, args: List[MObject]):
        arr, s, e = args
        return MValue(arr.value[s.value: e.value], None)


class Push(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(array: [Any], value: Any) -> [Any]")
        self.annotation = "Adds a value to the end of an array."

    def func(self, args: List[MObject]):
        arr, value = args
        arr.value.append(value)
        return arr


class Pop(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(array: [Any]) -> Any?")
        self.annotation = "Pops the last value from the array."

    def func(self, args: List[MObject]):
        arr = args[0]
        if len(arr.value) < 1:
            return MValue(None, "Can't pop value from empty array.")
        return arr.value.pop(-1)


class Shift(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(array: [Any], value: Any) -> [Any]")
        self.annotation = "Inserts a value at the front of an array."

    def func(self, args: List[MObject]):
        arr, value = args
        arr.value.insert(0, value)
        return arr


class Unshift(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(array: [Any]) -> Any?")
        self.annotation = "Pops the first value from the array."

    def func(self, args: List[MObject]):
        arr = args[0]
        if len(arr.value) < 1:
            return MValue(None, "Can't unshift value from an empty array.")
        return arr.value.pop(0)


class Delete(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(obj: {}, prop: Str) -> {}?")
        self.annotation = "Deletes a property from an object."

    def func(self, args: List[MObject]):
        obj, prop = args
        if prop.value not in obj.value:
            return MValue(None, f"The property '{prop.value}' does not exist.")
        del obj.value[prop.value]
        return obj


class Keys(MNativeFunction):
    class ObjectKeyIterator(MNativeFunction):
        def __init__(self, ip: Interpreter, obj: dict):
            super().__init__(ip, "fun(_: Null) -> Str?")
            self.annotation = "An object key iterator."
            self.array = []
            for key in obj.keys():
                keyval = MValue(key, None)
                self.array.append(keyval)
            self.index = 0

        def func(self, args: List[MObject]):
            index = self.index
            if index < len(self.array):
                self.index += 1
                return self.array[index]
            return MValue(None, None)
            
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(obj: {}) -> (Null -> Str?)")
        self.annotation = "Returns an iterator over an object's keys."

    def func(self, args: List[MObject]):
        arg = args[0]
        return Keys.ObjectKeyIterator(self.interpreter, arg.value)


class Values(MNativeFunction):
    class ObjectValueIterator(MNativeFunction):
        def __init__(self, ip: Interpreter, obj: dict):
            super().__init__(ip, "fun(_: Null) -> Any?")
            self.annotation = "An object key iterator."
            self.array = []
            for value in obj.values():
                self.array.append(value)
            self.index = 0

        def func(self, args: List[MObject]):
            index = self.index
            if index < len(self.array):
                self.index += 1
                return self.array[index]
            return MValue(None, None)
            
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(obj: {}) -> (Null -> Any?)")
        self.annotation = "Returns an iterator over an object's values."

    def func(self, args: List[MObject]):
        arg = args[0]
        return Values.ObjectValueIterator(self.interpreter, arg.value)

class Exists(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(obj: {}, key: Str) -> Bool")
        self.annotation = "Checks whether a key exists."

    def func(self, args: List[MObject]):
        obj, key = args
        return MValue(key.value in obj.value, None)
    
class Get(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(obj: {}, key: Str) -> Any?")
        self.annotation = "Returns a property."

    def func(self, args: List[MObject]):
        obj, key = args
        if key not in obj:
            return MValue(None, f"The property '{key}' does not exist.")
        return obj.value[key.value]

class Set(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(obj: {}, key: Str, value: Any) -> Any")
        self.annotation = "Set a property to a given value."

    def func(self, args: List[MObject]):
        obj, key, value = args
        obj.value[key.value] = value
        return value
