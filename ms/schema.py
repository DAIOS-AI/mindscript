import ms.ast as ast
from ms.objects import MType
import json

TABLEN = 4

class JSONSchema():

    def __init__(self):
        self.reset()

    def reset(self):
        self.prefix = ""
        self.indent = 0

    def indent_incr(self):
        self.indent += 1
        self.prefix = " " * self.indent * TABLEN

    def indent_decr(self):
        self.indent -= 1
        self.prefix = " " * self.indent * TABLEN

    # TODO
    def type_definition(self, node, optional=False, env=None):
        # Should not be called!
        raise ValueError("type_definition should not be called!")

    # TODO
    def type_annotation(self, node, optional=False, env=None):
        # Should not be called!
        raise ValueError("type_annotation should not be called!")

    def _resolve_type(self, t, env):
        resolving = True
        while resolving:
            if isinstance(t, ast.TypeAnnotation):
                t = t.expr
            elif isinstance(t, ast.TypeGrouping):
                t = t.expr
            elif isinstance(t, ast.TypeTerminal) and t.token.ttype == ast.TokenType.ID:
                key = t.token.literal
                value = env.get(key)
                t = value.value.definition
                env = value.value.env
            else:
                resolving = False
        return [t, env]


    # TODO: Solve for references.
    def type_terminal(self, node, optional=False, env=None):
        if node.token.ttype == ast.TokenType.ID:
            raise ValueError(f"TODO: Referencing {node.token.literal}.")
        elif node.token.ttype == ast.TokenType.TYPE:
            obj = {"type": None}
            if node.token.literal == "Int":
                obj["type"] = "integer"
            elif node.token.literal == "Num":
                obj["type"] = "number"
            elif node.token.literal == "Str":
                obj["type"] = "string"
            elif node.token.literal == "Bool":
                obj["type"] = "boolean"
            elif node.token.literal == "Null":
                obj["type"] = "null"
            elif node.token.literal == "Any":
                obj["type"] = ["array", "boolean", "number", "null", "object", "string"]
            if optional and type(obj["type"]) != list:
                obj["type"] = [obj["type"], "null"]
            if node.annotation is not None:
                obj["description"] = node.annotation
            schema = json.dumps(obj)
        else:
            raise ValueError("Unknown type!")
        return schema

    # TODO
    def type_grouping(self, node, optional=False, env=None):
        schema = node.expr.accept(self, env=env)
        return schema

    def type_unary(self, node, optional=False, env=None):
        schema = node.expr.accept(self, optional=True, env=env)
        return schema
    
    # TODO
    def type_binary(self, node, optional=False, env=None):
        print(f"schema.type_binary: node = {node}")
        self.indent_incr()
        left = node.left.accept(self, env=env)
        right = node.right.accept(self, env=env)
        content = left + "\n"
        content += self.prefix + " -> " + right + "\n"
        self.indent_decr()
        return content
    
    def type_array(self, node, optional=False, env=None):
        schema = '{\n'
        self.indent_incr()
        if node.annotation is not None:
            schema += self.prefix + f'"description": "{node.annotation}",\n'
        schema += self.prefix + '"type": "array",\n'
        schema += self.prefix + '"items": [\n'

        self.indent_incr()
        items = []
        for expr in node.array:
            subschema = self.prefix + expr.accept(self, env=env)
            items.append(subschema)
        schema += ",\n".join(items) + "\n"
        self.indent_decr()

        schema += self.prefix + ']\n'
        self.indent_decr()
        schema += self.prefix + '}'
        return schema

    def type_map(self, node, optional=False, env=None):
        required = []
        schema = '{\n'
        self.indent_incr()
        if node.annotation is not None:
            schema += self.prefix + f'"description": "{node.annotation}",\n'
        schema += self.prefix + '"type": "object",\n'
        schema += self.prefix + '"properties": {\n'

        self.indent_incr()
        items = []
        for key, expr in node.map.items():
            if key in node.required: required.append(key)
            subschema = self.prefix + f'"{key}": ' + expr.accept(self, env=env)
            items.append(subschema)
        schema += ",\n".join(items) + "\n"
        self.indent_decr()

        schema += self.prefix + '},\n'
        schema += self.prefix + '"required": ["' + '", "'.join(required) + '"]\n'
        self.indent_decr()
        schema += self.prefix + '}'
        return schema

    def print_schema(self, value):
        if type(value) != MType:
            return None
        schema = value.definition.accept(self, env=value.environment)
        return schema