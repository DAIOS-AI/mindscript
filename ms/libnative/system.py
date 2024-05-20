from typing import List, Any
from copy import deepcopy
import requests
from ms.objects import MNativeFunction, MValue, MObject
from ms.interpreter import Interpreter, Environment
from ms.types import TypeChecker
from ms.schema import JSONSchema
from ms.bnf import BNFFormatter
import ms.startup
import time
import datetime
import random

class TsNow(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(_: Null) -> Int")
        self.annotation = "Returns the current timestamp in milliseconds."

    def func(self, args: List[MObject]):
        now = round(time.time_ns() / 1000000)
        return MValue.wrap(now)

class DateNow(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(_: Null) -> Object")
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
        return MValue.wrap(date)

class Random(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(_: Null) -> Num")
        self.annotation = "Returns a uniform random variate."

    def func(self, args: List[MObject]):
        rand = random.random()
        return MValue.wrap(rand)