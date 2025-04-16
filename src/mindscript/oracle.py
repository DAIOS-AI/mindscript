import json
from typing import List, Any
from mindscript.schema import JSONSchema
from mindscript.bnf import BNFFormatter
from mindscript.objects import MType, MValue, MObject, MFunction
import mindscript.ast as ast


HEADER = """
You are a helpful assistant, and your task is to provide answers
respecting the format of the OUTPUT JSON SCHEMA. Do not put code
fences around the output (like ```json), only generate valid JSON.

INPUT JSON SCHEMA:

{input_schema}

OUTPUT JSON SCHEMA:

{output_schema}
"""

EXAMPLE = """
TASK:

{task}

INPUT:

{input}

OUTPUT:

{output}
"""

QUERY = """
TASK:

{task}

INPUT:

{input}

OUTPUT:

"""

# Main change to original implementation: Some backends only allow for
# structured outputs that are objects (i.e. no strings, numbers, nor arrays),
# hence we wrap the output spec into an object and unwrap the value from the response.


class MOracleFunction(MFunction):

    def __init__(self, ip: 'Interpreter', definition: ast.Function, examples: MValue):  # type: ignore
        super().__init__(ip, definition)

        jsonschema = JSONSchema(ip)
        bnf = BNFFormatter(ip)

        # Build a name (some backends need a unique id for an output schema).
        self.output_name = hex(id(self.outtype.definition))

        # Build input schemas.
        in_annotation = self.definition.types.annotation
        in_type_map = {param.literal: value.definition for param,
                       value in zip(self.params, self.intypes)}
        in_required = {param.literal: True for param in self.params}
        in_types = ast.TypeMap(annotation=in_annotation,
                               map=in_type_map, required=in_required)
        self.input_schema_str = jsonschema.print_schema(MType(ip, in_types))

        # Build output schema and BNF grammar.
        # We are also wrapping the schema into an object.
        try:
            out_type = self.outtype.definition
            unwrapped_schema = jsonschema.dict_schema(MType(ip, out_type))
            self.output_schema = {
                "type": "object",
                "properties": {"result": unwrapped_schema},
                "required": ["result"]
            }
            self.output_schema_str = json.dumps(self.output_schema)
            # self.output_grammar = bnf.format(MType(ip, out_type))
        except Exception as e:
            print("Exception:" + str(e))
        self.examples = self.validate_examples(examples)

        # Add null return.
        if type(self.outtype.definition) != ast.TypeUnary:
            self._outtype._definition = ast.TypeUnary(
                expr=self.outtype.definition)

        # Prepare prompt prefix.
        self.prompt_prefix = HEADER.format(input_schema=self.input_schema_str,
                                           output_schema=self.output_schema_str)
        self.prompt_prefix += self.prepare_examples()

    def prepare_input(self, args: List[MObject]):
        data = {}
        for param, arg in zip(self.params, args):
            data[param.literal] = arg
        return self.interpreter.print(MValue(data, None))

    def prepare_task(self):
        if self.definition.types.annotation:
            return self.definition.types.annotation
        return "Given the input, determine the output."

    def prepare_examples(self):
        task = self.prepare_task()
        body = ""
        for example in self.examples.value:
            input_example = self.prepare_input(example.value[:-1])
            output_example = self.interpreter.print(example.value[-1])
            body += EXAMPLE.format(task=task,
                                   input=input_example, output=output_example)
        return body

    def validate_examples(self, examples: MValue):
        if type(examples) != MValue or type(examples.value) != list:
            self.error("The examples must be of type [[Any]].")

        length = len(self.params) + 1
        for example in examples.value:
            if type(example.value) != list or len(example.value) != length:
                self.error(f"Each example must be an array of length {length}, "
                           f"but found {self.interpreter.print(example)}.")

            for n in range(len(self.params)):
                typestr = self.interpreter.print(self.intypes[n])
                valuestr = self.interpreter.print(example.value[n])
                if not self.interpreter.checktype(example.value[n], self.intypes[n]):
                    self.error(
                        f"Expected value of type '{typestr}' but found: {valuestr}.")

            if not self.interpreter.checktype(example.value[-1], self.outtype):
                typestr = self.interpreter.print(self.outtype)
                valuestr = self.interpreter.print(example.value[-1])
                self.error(
                    f"Expected output value of type '{typestr}' but found: {valuestr}.")
        return examples

    def func(self, args: List[MObject]):
        task = self.prepare_task()
        input_example = self.prepare_input(args)

        prompt = self.prompt_prefix
        prompt += QUERY.format(task=task, input=input_example)

        try:
            code = self.interpreter.backend.consult(self, prompt)
            json.loads(code) # Assert output is valid JSON.
            wrapped = self.interpreter.eval(code)
            output = wrapped.value["result"]
        except Exception as e:
            return MValue(None, str(e))
        return output

    def __repr__(self):
        return "<oracle>"

    def __str__(self):
        return "<oracle>"
