import requests
import dotenv
import os
import json
from typing import List, Any
from ms.schema import JSONSchema
from ms.objects import MType, MValue, MObject, MFunction
import ms.ast as ast

dotenv.load_dotenv()
api_key = os.getenv("TEXTSYNTH_API_KEY")
headers = {"Authorization": f"Bearer {api_key}"}
api_url = "https://api.textsynth.com/v1/engines/mixtral_47B_instruct/completions"


TEMPLATE = """
You are a helpful assistant, and your task is to provide answers
respecting the formatting instructions.

INPUT SCHEMA (JSON)
===================

{input_schema}

OUTPUT SCHEMA (JSON)
====================

{output_schema}

TASK DESCRIPTION
================

{task}

INPUT
=====

{input}

OUTPUT
======

"""


class MMagicFunction(MFunction):

    def __init__(self, ip: 'Interpreter', definition: ast.Function):  # type: ignore
        super().__init__(ip, definition)
        self._definition.expr = ast.Terminal(
            token=ast.Token(
                ttype=ast.TokenType.TYPE,
                literal="<magic function>"
            )

        )
        schema_printer = JSONSchema()
        self.input_schema = schema_printer.print_schema(
            MType(ip, definition.types.left))
        self.output_schema = schema_printer.print_schema(
            MType(ip, definition.types.right))
        self.output_schema_obj = json.loads(self.output_schema)
        self.output_annotation = definition.types.right.annotation

    def call(self, args: List[MObject]) -> MObject:
        if len(self.params) != len(args):
            raise ast.TypeError("Wrong number of parameters")
        for index in range(len(self.params)):
            if not self.interpreter.checktype(args[index], self.types[index]):
                raise ast.TypeError(f"Wrong type of function argument.")
        value = self.magic(args)
        value.annotation = self.output_annotation
        if not self.interpreter.checktype(value, self.types[-1]):
            raise ast.TypeError(f"Wrong type of function output.")
        return value

    def magic(self, args: List[MObject]):
        task = self.definition.types.annotation
        input_schema = self.input_schema
        output_schema = self.output_schema
        input = self.prepare_inputs(args)
        prompt = TEMPLATE.format(
            task=task, input=input, input_schema=input_schema, output_schema=output_schema)

        with requests.post(
            api_url, headers=headers,
            json={"prompt": prompt, "schema": json.loads(output_schema)}
        ) as response:
            response_obj = response.json()
            # print(f"magic: response = {response_obj}")
            response_txt = response_obj["text"]
            output = self.interpreter.eval(response_txt)

        # print(prompt + response_txt)
        return output

    def prepare_inputs(self, args: List[MObject]):
        inputs = [self.interpreter.printer.print(item) for item in args]
        if len(inputs) == 1:
            return inputs[0]
        return "[" + ", ".join(inputs) + "]"