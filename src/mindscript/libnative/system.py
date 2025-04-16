from typing import List, Any
from copy import deepcopy
import requests
from mindscript.objects import MNativeFunction, MValue, MObject
from mindscript.runtime import Interpreter, Environment
from mindscript.types import TypeChecker
from mindscript.schema import JSONSchema
from mindscript.bnf import BNFFormatter
import mindscript.builtins
import time
import datetime
import random
import mindscript

class TsNow(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(_: Null) -> Int")
        self.annotation = "Returns the current timestamp in milliseconds."

    def func(self, args: List[MObject]):
        now = round(time.time_ns() / 1000000)
        return mindscript.wrap(now)

class DateNow(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(_: Null) -> {}")
        self.annotation = "Returns a the current date."

    def func(self, args: List[MObject]):
        now = datetime.datetime.now()
        date = {
            "year": now.year,
            "month": now.month,
            "day": now.day,
            "hour": now.hour,
            "second": now.second,
            "millisecond": now.microsecond
        }
        return mindscript.wrap(date)

class Random(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(_: Null) -> Num")
        self.annotation = "Returns a uniform random variate."

    def func(self, args: List[MObject]):
        rand = random.random()
        return mindscript.wrap(rand)