from typing import List, Any
from copy import deepcopy
from ms.objects import MNativeFunction, MValue, MObject
from ms.interpreter import Interpreter, Environment
from ms.types import TypeChecker
from ms.schema import JSONSchema
from ms.bnf import BNFFormatter
import ms.startup
from ms.libnative.auxiliary import import_code, flattened_env


class Import(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(filename: Str) -> {}")
        self.annotation = "Imports a file at a given path as a module."

    def func(self, args: List[MObject]):
        filename = args[0].value
        try:
            with open(filename, "r") as fh:
                code = fh.read()
            module = import_code(code)
        except FileNotFoundError as e:
            self.error(f"File not found: {filename}")
        except Exception as e:
            self.error(str(e))
        return MValue(module, None)
    
