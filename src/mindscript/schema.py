import mindscript.ast as ast
from mindscript.objects import MType, unwrap
import json
import re

TABLEN = 4


class JSONSchema():

    def __init__(self, interpreter):
        self.interpreter = interpreter

    # TODO
    def type_definition(self, node, env=None, visited=None):
        # Should not be called!
        raise ValueError("type_definition should not be called!")

    # TODO
    def type_annotation(self, node, env=None, visited=None):
        # Should not be called!
        raise ValueError("type_annotation should not be called!")

    def _resolve_ref(self, name, env=None, visited=None):
        try:
            res = env.get(name)
        except KeyError:
            raise KeyError(f"Unknown type '{name}'.")
        if type(res) != MType:
            raise ValueError(f"The value '{name}' is not a type.")
        node = res.definition
        identifier = id(node)
        if identifier in visited:
            raise ValueError(f"Recursive types such as '{name}' are not allowed.")        
        visited.append(identifier)
        return node

    # TODO: Solve for references.
    def type_terminal(self, node, env=None, visited=[]):
        obj = {}
        if node.token.ttype == ast.TokenType.ID:
            new_node = self._resolve_ref(node.token.literal, env, visited)
            return new_node.accept(self, env=env, visited=visited)
        elif node.token.ttype == ast.TokenType.TYPE:
            obj["type"] = None
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
            if node.annotation is not None:
                obj["description"] = node.annotation
        else:
            raise ValueError("Unknown type!")
        return obj

    def type_grouping(self, node, env=None, visited=None):
        obj = node.expr.accept(self, env=env, visited=visited)
        return obj

    def type_unary(self, node, env=None, visited=None):
        obj = node.expr.accept(self, env=env, visited=visited)
        if type(obj["type"]) == str:
            obj["type"] = [obj["type"], "null"] 
        if type(obj["type"]) == list and "null" not in obj:
            obj["type"] = obj["type"].append("null")
        return obj

    # TODO
    def type_binary(self, node, env=None, visited=None):
        raise NotImplementedError("JSON Schemas for function types are not implemented yet.")

    def type_enum(self, node, env=None, visited=None):
        obj = {}
        obj["enum"] = unwrap(node.values)
        if node.annotation is not None:
            obj["description"] = node.annotation
        return obj

    def type_array(self, node, env=None, visited=None):
        obj = {}
        obj["type"] = "array"
        if node.annotation is not None:
            obj["description"] = node.annotation
        obj["items"] = node.expr.accept(self, env=env, visited=visited)
        return obj

    def type_map(self, node, env=None, visited=None):
        obj = {}
        obj["type"] = "object"
        if node.annotation is not None:
            obj["description"] = node.annotation
        obj["required"] = []
        obj["properties"] = {}
        for key, expr in node.map.items():
            if key in node.required:
                obj["required"].append(key)
            obj["properties"][key] = expr.accept(self, env=env, visited=visited)
        return obj

    def dict_schema(self, value):
        if type(value) != MType:
            return None
        visited = [id(value.definition)]
        schema = value.definition.accept(self, env=value.environment, visited=visited)
        return schema
    
    def print_schema(self, value):
        schema = self.dict_schema(value)
        if schema is None:
            return None
        return json.dumps(schema, indent=4)
