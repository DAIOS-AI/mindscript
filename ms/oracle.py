import requests
import os
import json
from typing import List, Any
from ms.schema import JSONSchema
from ms.bnf import BNFFormatter
from ms.objects import MType, MValue, MObject, MFunction
import ms.ast as ast


max_tokens = 1000

api_url = "http://localhost:8080/completion"
headers = {"Content-Type": "application/json"}


HEADER = """
You are a helpful assistant, and your task is to provide answers
respecting the formatting instructions.

INPUT SCHEMA (JSON)
===================

{input_schema}

OUTPUT SCHEMA (JSON)
====================

{output_schema}
"""

EXAMPLE = """
TASK
====

{task}

INPUT
=====

{input}

OUTPUT
======

{output}
"""

QUERY = """
TASK
====

{task}

INPUT
=====

{input}

OUTPUT
======

"""


class MOracleFunction(MFunction):

    def __init__(self, ip: 'Interpreter', definition: ast.Function, examples: MValue):  # type: ignore
        super().__init__(ip, definition)

        schema_printer = JSONSchema()
        bnf_printer = BNFFormatter()

        # Build input schemas.
        in_annotation = self.definition.types.annotation
        in_type_map = {param.literal: value.definition for param,
                       value in zip(self.params, self.intypes)}
        in_required = {param.literal: True for param in self.params}
        in_types = ast.TypeMap(annotation=in_annotation,
                               map=in_type_map, required=in_required)
        self.input_schema = schema_printer.print_schema(MType(ip, in_types))

        # Build output schema and BNF grammar.
        out_type = self.outtype.definition
        self.output_schema = schema_printer.print_schema(MType(ip, out_type))
        self.output_schema_obj = bnf_printer.format(MType(ip, out_type))
        # self.output_schema_obj = self.output_schema #json.loads(self.output_schema)

        self.examples = self.validate_examples(examples)

    def prepare_input(self, args: List[MObject]):
        data = {}
        for param, arg in zip(self.params, args):
            data[param.literal] = arg
        return self.interpreter.print(MValue(data, None))

    def prepare_task(self):
        if self.definition.types.annotation:
            return self.definition.types.annotation
        return "Determine the output from the input."

    def prepare_examples(self):
        task = self.prepare_task()
        body = ""
        for example in self.examples.value:
            input_example = self.prepare_input(example.value[:-1])
            output_example = self.interpreter.print(example.value[-1])
            body += EXAMPLE.format(task=task, input=input_example, output=output_example)
        return body

    def validate_examples(self, examples: MValue):
        if type(examples) != MValue or type(examples.value) != list:
            self.error("The examples must be of type Array[Array].")

        length = len(self.params) + 1
        for example in examples.value:
            if type(example.value) != list or len(example.value) != length:
                self.error(f"Each example must be an array of length {length}, "
                           f"but found {self.interpreter.print(example)}.")

            for n in range(len(self.params)):
                typestr = self.interpreter.print(self.intypes[n])
                valuestr = self.interpreter.print(example.value[n])
                if not self.interpreter.checktype(example.value[n], self.intypes[n]):
                    self.error(f"Expected value of type {typestr} but found: {valuestr}.")

            if not self.interpreter.checktype(example.value[-1], self.outtype):
                typestr = self.interpreter.print(self.outtype)
                valuestr = self.interpreter.print(example.value[-1])
                self.error(f"Expected output value of type {typestr} but found: {valuestr}.")
        return examples

    def func(self, args: List[MObject]):
        task = self.prepare_task()
        input_schema = self.input_schema
        output_schema = self.output_schema
        input_example = self.prepare_input(args)

        prompt = HEADER.format(input_schema=input_schema, output_schema=output_schema)
        prompt += self.prepare_examples()
        prompt += QUERY.format(task=task, input=input_example)

        # print(f"oracle: prompt = {prompt}")
        with requests.post(
            api_url, headers=headers,
            json={
                "prompt": prompt,
                # "json_schema": self.output_schema_obj,
                "grammar": self.output_schema_obj,
                "n_predit": max_tokens,
                "repeat_penalty": 1.5
            }
        ) as response:
            response_obj = response.json()
            # print(f"\noracle: response = {response_obj}")
            response_txt = response_obj["content"]
            output = self.interpreter.eval(response_txt)

        # print(prompt + response_txt)
        return output

    def __repr__(self):
        # print(f"UserFunction.repr: definition = {self.definition}")
        return "<oracle>"

    def __str__(self):
        # print(f"UserFunction.str: definition = {self.definition}")
        return "<oracle>"
