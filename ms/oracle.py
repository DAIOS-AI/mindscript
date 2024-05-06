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

# api_url = "http://localhost:8080/completion"
# headers = {"Content-Type": "application/json"}


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


class MOracleFunction(MFunction):

    def __init__(self, ip: 'Interpreter', definition: ast.Function):  # type: ignore
        super().__init__(ip, definition)
        self._definition.expr = ast.Terminal(
            token=ast.Token(
                ttype=ast.TokenType.TYPE,
                literal="<oracle function>"
            )

        )
        schema_printer = JSONSchema()
        in_annotation = self.definition.types.annotation
        in_type_map = {param.literal: value.definition for param, value in zip(self.params, self.intypes)}
        in_required = {param.literal: True for param in self.params}
        in_types = ast.TypeMap(annotation=in_annotation, map=in_type_map, required=in_required)
        self.input_schema = schema_printer.print_schema(MType(ip, in_types))

        out_type = self.outtype.definition
        self.output_schema = schema_printer.print_schema(MType(ip, out_type))
        self.output_schema_obj = json.loads(self.output_schema)

    def prepare_input(self, args: List[MObject]):
        data = {}
        for param, arg in zip(self.params, args):
            data[param.literal] = arg
        return self.interpreter.printer.print(MValue(data, None))

    def func(self, args: List[MObject]):
        task = self.definition.types.annotation
        input_schema = self.input_schema
        output_schema = self.output_schema
        input = self.prepare_input(args)
        prompt = TEMPLATE.format(
            task=task, input=input, input_schema=input_schema, output_schema=output_schema)
        print(f"oracle: prompt = {prompt}")
        with requests.post(
            api_url, headers=headers,
            json={"prompt": prompt, "schema": self.output_schema_obj}
        ) as response:
            response_obj = response.json()
            print(f"oracle: response = {response_obj}")
            response_txt = response_obj["text"]
            # response_txt = response_obj["content"]
            output = self.interpreter.eval(response_txt)

        # print(prompt + response_txt)
        return output


