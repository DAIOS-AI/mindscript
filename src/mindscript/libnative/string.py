from typing import List
from mindscript.objects import MNativeFunction, MValue, MObject
from mindscript.runtime import Interpreter
import re

# String Manipulation:
# Concatenation, substring extraction: concat, substring
# Case conversion: to_upper, to_lower
# Trimming: trim, ltrim, rtrim
# Splitting and joining: split, join
# Pattern matching: match, replace

class SubStr(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(string: Str, s: Int, e: Int) -> Str")
        self.annotation = "Substring function"

    def func(self, args: List[MObject]):
        string, s, e = args
        return MValue(string.value[s.value: e.value], None)

class ToUpper(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(string: Str) -> Str")
        self.annotation = "Converts a string to uppercase."

    def func(self, args: List[MObject]):
        arg = args[0]
        return MValue(arg.value.upper(), None)

class ToLower(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(string: Str) -> Str")
        self.annotation = "Converts a string to lowercase."

    def func(self, args: List[MObject]):
        arg = args[0]
        return MValue(arg.value.lower(), None)

class Strip(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(string: Str) -> Str")
        self.annotation = "Removes leading and trailing whitespace."

    def func(self, args: List[MObject]):
        arg = args[0]
        return MValue(arg.value.strip(), None)

class LStrip(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(string: Str) -> Str")
        self.annotation = "Removes leading whitespace."

    def func(self, args: List[MObject]):
        arg = args[0]
        return MValue(arg.value.lstrip(), None)

class RStrip(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(string: Str) -> Str")
        self.annotation = "Removes trailing whitespace."

    def func(self, args: List[MObject]):
        arg = args[0]
        return MValue(arg.value.rstrip(), None)

class Split(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(string: Str, separator: Str) -> [Str]")
        self.annotation = "Splits a string into a list of string using a separator."

    def func(self, args: List[MObject]):
        string, separator = args
        splits = string.value.split(separator.value)
        splits = [MValue(s, None) for s in splits]
        return MValue(splits, None)

class Join(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(strings: [Str], separator: Str) -> Str")
        self.annotation = "Joins strings into a single string using a separator."

    def func(self, args: List[MObject]):
        strings, separator = args
        join = separator.value.join([s.value for s in strings.value])
        return MValue(join, None)

class Match(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(pattern: Str, string: Str) -> [Str]")
        self.annotation = "Searches for a regex pattern within a string and returns a list of matches."

    def func(self, args: List[MObject]):
        pattern, string = args
        match = re.findall(pattern.value, string.value)
        match = [MValue(s, None) for s in match]
        return MValue(match, None)

class Replace(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(pattern: Str, replace: Str, string: Str) -> Str")
        self.annotation = "Substitutes a regex pattern with a replacement within a string."

    def func(self, args: List[MObject]):
        pattern, replace, string = args
        result = re.sub(pattern.value, replace.value, string.value)
        return MValue(result, None)
