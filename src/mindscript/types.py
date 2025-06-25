import mindscript.ast as ast
from mindscript.objects import MObject, MValue, MFunction, MType

class TypeChecker():

    def __init__(self, ip):
        self.interpreter = ip

    def _checktype_recursion(self, value, target, env):

        # Check if both types are the same primitive type
        if type(target) == ast.TypeTerminal and target.token.literal == "Any":
            return True

        if type(target) == ast.TypeTerminal and target.token.ttype == ast.TokenType.ID:
            name = target.token.literal
            try:
                new_target = env.get(name)
            except KeyError:
                raise KeyError(f"Unknown type '{name}'.")
            if type(new_target) != MType:
                raise ValueError(f"Referencing '{name}', which is not a type.")
            return self._checktype_recursion(value, new_target.definition, new_target.environment)

        if type(value) == MValue:
            v = value.value
            if type(target) == ast.TypeTerminal and target.token.ttype == ast.TokenType.TYPE:
                if v is None and target.token.literal == "Null":
                    return True
                elif type(v) == bool and target.token.literal == "Bool":
                    return True
                elif type(v) == int and target.token.literal == "Int":
                    return True
                elif (type(v) == int or type(v) == float) and target.token.literal == "Num":
                    return True
                elif type(v) == str and target.token.literal == "Str":
                    return True
            elif type(v) == list and type(target) == ast.TypeArray:
                starget = target.expr
                if all(self._checktype_recursion(svalue, starget, env) for svalue in value.value):
                    return True
                return False
            elif type(v) == dict and type(target) == ast.TypeMap:
                required = list(target.required.keys())
                for key in target.map.keys():
                    if key in v:
                        if not self._checktype_recursion(v[key], target.map[key], env):
                            return False
                    elif key not in v and key in required:
                        return False
                    if key in v and key in required:
                        required.remove(key)
                if len(required) > 0:
                    return False
                return True
            elif type(target) == ast.TypeEnum:
                for allowed in target.values.value:
                    if self.interpreter.compare(value, allowed):
                        return True
                return False
            elif type(target) == ast.TypeUnary:
                if v is None:
                    return True
                else:
                    return self._checktype_recursion(value, target.expr, env)
            return False
        elif type(value) == MType and type(target) == ast.TypeTerminal and target.token.literal == "Type":
            return True
        elif isinstance(value, MFunction):
            fdef = value.definition.types
            fenv = value.interpreter.env
            return self._subtype_recursion(t1=fdef, t2=target, env1=fenv, env2=env)
        return False
    
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

        elif type1 == ast.TypeArray and type2 == ast.TypeArray:
            return self._subtype_recursion(t1.expr, t2.expr, env1, env2, visited)

        elif type1 == ast.TypeMap and type2 == ast.TypeMap:
            if not set(t2.required.keys()).issubset(set(t1.required.keys())):
                return False
            for key in t1.map.keys():
                if key in t2.map.keys() and not self._subtype_recursion(t1.map[key], t2.map[key], env1, env2):
                    return False
            return True
        
        elif type1 == ast.TypeEnum and type2 != ast.TypeEnum:
            for val in t1.values.value:
                if not self._checktype_recursion(val, t2, env2):
                    return False
            return True
        elif type1 == ast.TypeEnum and type2 == ast.TypeEnum:
            # TODO: Proper comparison of Enums requires comparing their contents,
            # which in the ideal, efficient case would require additional machinery
            # (e.g. recurisve value hashing). We'll brute-force here.
            for val1 in t1.values.value:
                found = False
                for val2 in t2.values.value:
                    if self.interpreter.compare(val1, val2):
                        found = True
                        break
                if not found:
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
            elif type(v) == bool:
                valtype = ast.TypeTerminal(token=ast.Token(
                    ttype=ast.TokenType.TYPE, literal="Bool"))
            elif type(v) == str:
                valtype = ast.TypeTerminal(token=ast.Token(
                    ttype=ast.TokenType.TYPE, literal="Str"))
            elif type(v) == int:
                valtype = ast.TypeTerminal(token=ast.Token(
                    ttype=ast.TokenType.TYPE, literal="Int"))
            elif type(v) == float:
                valtype = ast.TypeTerminal(token=ast.Token(
                    ttype=ast.TokenType.TYPE, literal="Num"))
            elif type(v) == list:
                # TODO: We need to find a representative type for the list. The correct way of doing this
                # is using Unification. But here we follow a simple approach.
                # 1) If the list is empty, then type is Array.
                # 2) Pick the first item's type and set is as the most general type (m.g.t).
                # 3) For each item: if its type is a subtype of the m.g.t., keep the m.g.t.
                #    If instead the m.g.t. is a subtype of the item's type, use the latter as the m.g.t.
                #    If neither of the above works, set m.g.t. Any.
                # 4) Ignore nulls: just mark as nullable in case m.g.t. isn't Any.
                items = []
                nullable = False
                anytype = False
                if len(v) == 0:
                    valtype = ast.TypeArray(
                        expr=ast.TypeTerminal(
                            token=ast.Token(
                                ttype=ast.TokenType.TYPE, literal="Any")))
                else:
                    gtype = None 
                    for item in v:
                        subtype = self._typeof_recursion(item)
                        if type(subtype) == ast.TypeTerminal and subtype.token.literal == "Null":
                            nullable = True
                            continue
                        if gtype is None:
                            gtype = subtype
                            continue
                        if not self._subtype_recursion(subtype, gtype, None, None):
                            if self._subtype_recursion(gtype, subtype, None, None):
                                gtype = subtype
                            else:
                                anytype = True
                                break
                    if anytype:
                        gtype = ast.TypeTerminal(token=ast.Token(ttype=ast.TokenType.TYPE, literal="Any"))
                    elif gtype is None:
                        gtype = ast.TypeTerminal(token=ast.Token(ttype=ast.TokenType.TYPE, literal="Null"))
                    elif nullable:
                        gtype = ast.TypeUnary(expr=gtype)
                    valtype = ast.TypeArray(expr=gtype)
            elif type(v) == dict:
                items = {}
                for key, item in v.items():
                    subtype = self._typeof_recursion(item)
                    items[key] = subtype
                else:
                    valtype = ast.TypeMap(map=items, required={})
        elif isinstance(value, MFunction):
            valtype = value.definition.types
        elif isinstance(value, MType):
            valtype = ast.TypeTerminal(token=ast.Token(
                ttype=ast.TokenType.TYPE, literal="Type"))
        else:
            "print_value: Unknown value type!"
        return valtype

    def typeof(self, value: MObject) -> ast.TypeExpr:
        return self._typeof_recursion(value)

    def checktype(self, value: MObject, target: MType) -> bool:
        if type(target) != MType:
            return False
        return self._checktype_recursion(value, target.definition, target.environment)

    def issubtype(self, subtype: MObject, supertype: MObject) -> bool:
        if type(subtype) != MType or type(supertype) != MType:
            return False
        t1 = subtype.definition
        env1 = subtype.environment
        t2 = supertype.definition
        env2 = supertype.environment
        return self._subtype_recursion(t1=t1, t2=t2, env1=env1, env2=env2)
