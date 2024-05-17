from typing import Optional, Any, List
import ms.ast as ast
from ms.objects import MObject, MValue, MFunction, MType

class TypeChecker():

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
                if type(value) != MType:
                    raise ValueError(f"Referencing '{key}', which is not a type.")
                t = value.definition
                env = value.environment
            else:
                resolving = False
        return [t, env]

    def _subtype_recursion(self, t1, t2, env1, env2, visited=None):
        if visited is None:
            visited = set()

        # Resolve type aliases and annotations.
        [t1, env1] = self._resolve_type(t1, env1)
        [t2, env2] = self._resolve_type(t2, env2)

        # Check for recursion
        if (id(t1), id(t2)) in visited or (id(t2), id(t1)) in visited:
            return True
        visited.add((id(t1), id(t2)))

        type1 = type(t1)
        type2 = type(t2)

        # Check if both types are the same primitive type
        if type2 == ast.TypeTerminal and t2.token.literal == "Any":
            return True
        elif type1 == ast.TypeTerminal and type2 == ast.TypeTerminal:
            if t1.token.literal == t2.token.literal:
                return True

        elif type1 == ast.TypeArray and type2 == ast.TypeTerminal and t2.token.literal == "Array":
            return True
        elif type1 == ast.TypeArray and type2 == ast.TypeArray:
            if len(t1.array) != 1 and len(t2.array) == 1:
                return all(
                    self._subtype_recursion(sub, t2.array[0], env1, env2, visited)
                    for sub in t1.array
                )
            if len(t1.array) != len(t2.array):
                return False
            return all(
                self._subtype_recursion(sub1, sub2, env1, env2, visited)
                for sub1, sub2 in zip(t1.array, t2.array)
            )

        elif type1 == ast.TypeMap and type2 == ast.TypeTerminal and t2.token.literal == "Object":
            return True
        elif type1 == ast.TypeMap and type2 == ast.TypeMap:
            if not set(t1.map.keys()).issubset(set(t2.map.keys())):
                return False
            for key in t2.map.keys():
                if key not in t1.map:
                    nulltype = ast.Terminal(
                        token=ast.Token(
                            ttype=ast.TokenType.TYPE, literal="Null"))
                    valid = self._subtype_recursion(
                        nulltype, t2.map[key], env1, env2, visited)
                else:
                    valid = self._subtype_recursion(
                        t1.map[key], t2.map[key], env1, env2, visited)
                if not valid:
                    return False
            return True

        elif type2 == ast.TypeUnary:
            if type1 == ast.TypeUnary:
                return self._subtype_recursion(t1.expr, t2.expr, env1, env2, visited)
            elif type1 == ast.TypeTerminal and t1.token.literal == "Null":
                return True
            return self._subtype_recursion(t1, t2.expr, env1, env2, visited)

        elif type1 == ast.TypeBinary and type2 == ast.TypeBinary:
            return (self._subtype_recursion(t1.left, t2.left, env1, env2, visited)
                    and self._subtype_recursion(t1.right, t2.right, env1, env2, visited))

        return False

    def _typeof_recursion(self, value) -> ast.TypeExpr:
        valtype = None
        if isinstance(value, MValue):
            v = value.value
            if v is None:
                valtype = ast.TypeTerminal(token=ast.Token(
                    ttype=ast.TokenType.TYPE, literal="Null"))
            elif type(v) == str:
                valtype = ast.TypeTerminal(token=ast.Token(
                    ttype=ast.TokenType.TYPE, literal="Str"))
            elif type(v) == int:
                valtype = ast.TypeTerminal(token=ast.Token(
                    ttype=ast.TokenType.TYPE, literal="Int"))
            elif type(v) == float:
                valtype = ast.TypeTerminal(token=ast.Token(
                    ttype=ast.TokenType.TYPE, literal="Num"))
            elif type(v) == bool:
                valtype = ast.TypeTerminal(token=ast.Token(
                    ttype=ast.TokenType.TYPE, literal="Bool"))
            elif type(v) == list:
                items = []
                for item in v:
                    subtype = self._typeof_recursion(item)
                    items.append(subtype)
                valtype = ast.TypeArray(array=items)
            elif type(v) == dict:
                items = {}
                for key, item in v.items():
                    subtype = self._typeof_recursion(item)
                    items[key] = subtype
                valtype = ast.TypeMap(map=items, required={})
        elif isinstance(value, MFunction):
            # print(f"typechecker._typeof_recursion: v.definition.types = {v.definition.types}")
            valtype = value.definition.types
        elif isinstance(value, MType):
            valtype = ast.TypeTerminal(token=ast.Token(
                ttype=ast.TokenType.TYPE, literal="Type"))
        else:
            "print_value: Unknown value type!"
        return valtype

    def typeof(self, value: MObject) -> ast.TypeExpr:
        return self._typeof_recursion(value)

    def issubtype(self, subtype: MObject, supertype: MObject) -> bool:
        if type(subtype) != MType or type(supertype) != MType:
            return False
        t1 = subtype.definition
        env1 = subtype.interpreter.env
        t2 = supertype.definition
        env2 = supertype.interpreter.env
        return self._subtype_recursion(t1=t1, t2=t2, env1=env1, env2=env2)
