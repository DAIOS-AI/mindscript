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
        self.input_schema = schema_printer.print_schema(
            MType(ip, definition.types.left))
        self.output_schema = schema_printer.print_schema(
            MType(ip, definition.types.right))
        self.output_schema_obj = json.loads(self.output_schema)
        self.output_annotation = definition.types.right.annotation

    def func(self, arg: MObject):
        task = self.definition.types.annotation
        input_schema = self.input_schema
        output_schema = self.output_schema
        input = self.interpreter.printer.print(arg)
        prompt = TEMPLATE.format(
            task=task, input=input, input_schema=input_schema, output_schema=output_schema)

        with requests.post(
            api_url, headers=headers,
            json={"prompt": prompt, "schema": json.loads(output_schema)}
        ) as response:
            response_obj = response.json()
            # print(f"oracle: response = {response_obj}")
            response_txt = response_obj["text"]
            output = self.interpreter.eval(response_txt)

        # print(prompt + response_txt)
        return output


