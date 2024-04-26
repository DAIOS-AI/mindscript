from typing import Optional, Any, List, Callable
import ms.ast as ast
from ms.printer import Printer
from ms.parser import Parser
from ms.types import TypeChecker
from ms.objects import MObject, MValue, MType, MFunction, MUserFunction, Environment
from ms.magic import MMagicFunction


class Interpreter:

    def __init__(self, interactive=False):
        self.printer = Printer()
        self.parser = Parser(interactive=interactive)
        self.checker = TypeChecker()
        self.reset()

    def reset(self):
        self.parser.reset()
        self.env = Environment()

    def eval(self, instr: str):
        val = MValue(None, None)
        tree = self.parser.parse(instr)
        if tree is None:
            return val
        try:
            val = tree.accept(self)
        except ast.Return as e:
            return e.expr
        except (ast.Break, ast.Continue) as e:
            self.parser.lexer.report_error(
                e.operator.line,
                e.operator.col,
                "RUNTIME ERROR",
                f"Unexpected control flow expression '{e.operator.literal}'.")
        except RuntimeError as e:
            pass
        return val

    def typeof(self, value: MObject) -> MType:
        definition = self.checker.typeof(value)
        return MType(self, definition)
    
    def issubtype(self, subtype: MObject, supertype: MObject) -> bool:
        res = self.checker.issubtype(subtype, supertype)
        return res

    def checktype(self, value: MObject, required: MType) -> bool:
        value_type = self.typeof(value)
        return self.issubtype(value_type, required)

    def define(self, name: str, value: MValue):
        self.env.define(name, value)

    def error(self, token: ast.Token, msg):
        self.parser.lexer.report_error(
            token.line, token.col, "RUNTIME ERROR", msg)
        raise RuntimeError(msg)

    def program(self, node: ast.Expr):
        value = None
        exprs = node.program
        for expr in exprs:
            value = expr.accept(self)
        return value

    def annotation(self, node: ast.Expr):
        annotation = node.annotation.literal
        value = node.expr.accept(self)
        value.annotation = annotation
        return value

    def binary(self, node: ast.Expr):

        operator = node.operator

        # Short-circuit operators.
        if operator.ttype == ast.TokenType.OR:
            lvalue = node.left.accept(self).value
            if type(lvalue) != bool:
                self.error(operator, "Operands must be boolean.")
            if lvalue:
                return MValue(True, None)
            rvalue = node.right.accept(self).value
            if type(rvalue) == bool:
                return MValue(rvalue, None)
            self.error(operator, "Operands must be boolean.")

        if operator.ttype == ast.TokenType.AND:
            lvalue = node.left.accept(self).value
            if type(lvalue) != bool:
                self.error(operator, "Operands must be boolean.")
            if not lvalue:
                return MValue(False, None)
            rvalue = node.right.accept(self).value
            if type(rvalue) == bool:
                return MValue(rvalue, None)
            self.error(operator, "Operands must be boolean.")

        # Standard operators.
        lvalue = node.left.accept(self).value
        rvalue = node.right.accept(self).value

        if ((type(lvalue) == int or type(lvalue) == float)
                and (type(rvalue) == int or type(rvalue) == float)):

            if operator.ttype == ast.TokenType.PLUS:
                return MValue(lvalue + rvalue, None)
            elif operator.ttype == ast.TokenType.MINUS:
                return MValue(lvalue - rvalue, None)
            elif operator.ttype == ast.TokenType.MULT:
                return MValue(lvalue * rvalue, None)
            elif operator.ttype == ast.TokenType.DIV:
                return MValue(lvalue / rvalue, None)
            elif operator.ttype == ast.TokenType.MOD:
                return MValue(lvalue % rvalue, None)
            elif operator.ttype == ast.TokenType.GREATER:
                return MValue(lvalue < rvalue, None)
            elif operator.ttype == ast.TokenType.GREATER_EQ:
                return MValue(lvalue <= rvalue, None)
            elif operator.ttype == ast.TokenType.LESS:
                return MValue(lvalue < rvalue, None)
            elif operator.ttype == ast.TokenType.LESS_EQ:
                return MValue(lvalue <= rvalue, None)
            elif operator.ttype == ast.TokenType.EQ:
                return MValue(lvalue == rvalue, None)
            elif operator.ttype == ast.TokenType.NEQ:
                return MValue(lvalue != rvalue, None)
            self.error(
                operator, "Unexpected operator for integer/number operands.")

        elif type(lvalue) == bool and type(rvalue) == bool:
            if operator.ttype == ast.TokenType.EQ:
                return MValue(lvalue == rvalue, None)
            elif operator.ttype == ast.TokenType.NEQ:
                return MValue(lvalue != rvalue, None)
            self.error(operator, "Unexpected operator for boolean operands.")

        elif type(rvalue) == str and type(lvalue) == str:
            if operator.ttype == ast.TokenType.PLUS:
                return MValue(lvalue + rvalue, None)
            elif operator.ttype == ast.TokenType.GREATER:
                return MValue(lvalue > rvalue, None)
            elif operator.ttype == ast.TokenType.GREATER_EQ:
                return MValue(lvalue >= rvalue, None)
            elif operator.ttype == ast.TokenType.LESS:
                return MValue(lvalue < rvalue, None)
            elif operator.ttype == ast.TokenType.LESS_EQ:
                return MValue(lvalue <= rvalue, None)
            elif operator.ttype == ast.TokenType.EQ:
                return MValue(lvalue == rvalue, None)
            elif operator.ttype == ast.TokenType.NEQ:
                return MValue(lvalue != rvalue, None)
            self.error(operator, "Unexpected operator for string operands.")

        self.error(operator, "Inconsistent operands.")

    def unary(self, node: ast.Expr):
        operator = node.operator
        expr = node.expr.accept(self)
        value = expr.value
        if operator.ttype == ast.TokenType.NOT:
            if type(value) == bool:
                return MValue(not value, None)
            self.error(operator, "Expected a boolean.")
        elif operator.ttype == ast.TokenType.MINUS:
            if type(value) == int or type(value) == float:
                return MValue(-value, None)
            self.error(operator, "Expected a number.")
        elif operator.ttype == ast.TokenType.RETURN:
            raise ast.Return(operator, expr)
        elif operator.ttype == ast.TokenType.BREAK:
            raise ast.Break(operator, expr)
        elif operator.ttype == ast.TokenType.CONTINUE:
            raise ast.Continue(operator, expr)
        elif operator.ttype == ast.TokenType.QUESTION:
            if type(expr) == MType:
                usertype = MType(self, ast.Unary(
                    operator=operator, expr=expr.definition))
                return MValue(usertype, None)
            self.error(operator, "Expected a preceding type.")
        self.error(operator, "Wrong unary operation.")

    def grouping(self, node: ast.Expr):
        expr = node.expr.accept(self)
        return expr

    def terminal(self, node: ast.Expr):
        if node.token.ttype == ast.TokenType.ID:
            identifier = node.token.literal
            try:
                return self.env.get(identifier)
            except KeyError:
                self.error(node.token, "Undefined variable.")
        value = node.token.literal
        return MValue(value, None)

    def array_get(self, node: ast.Expr):
        # expr, index
        operator = node.operator
        getter = node.expr.accept(self).value
        index = node.index.accept(self).value
        if type(getter) == list:
            if type(index) == int:
                if abs(index) < len(getter):
                    index = index % len(getter)
                    return getter[index]
                self.error(operator, "Array index out of range.")
            self.error(operator, "Array index must be an integer.")
        self.error(operator, "Attempted to access a member on a non-array.")

    def object_get(self, node: ast.Expr):
        # expr, index
        operator = node.operator
        getter = node.expr.accept(self).value
        index = node.index.accept(self).value
        if type(getter) == dict and type(index) == str:
            if index in getter:
                return getter[index]
            self.error(operator, f"Unknown property '{index}'.")
        self.error(operator, "Attempted to access a property on a non-object.")

    def set(self, node: ast.Expr):
        # This should never be called directly.
        self.error(node.index, "Set should not be interpreted directly.")

    def assign_search(self, env, target, operator, value):
        if isinstance(target, ast.Terminal):
            identifier = target.token.literal
            try:
                env.set(identifier, value)
            except KeyError:
                self.error(
                    operator, "Attempted to assign to an uninitialized variable.")
            return value
        elif isinstance(target, ast.Annotation):
            # Push the annotation into the value!
            annotation = target.annotation.literal
            value.annotation = annotation
            return self.assign_search(env, target.expr, operator, value)
        elif isinstance(target, ast.Declaration):
            # Capture inner declaration!
            identifier = target.token.literal
            env.define(identifier, value)
            return value
        elif isinstance(target, ast.ObjectSet):
            setter = target.expr.accept(self).value
            index = target.index.accept(self).value
            if type(index) == str and index in setter:
                setter[index] = value
                return value
            self.error(
                operator, "Attempted to assign to an unknown property.")
        elif isinstance(target, ast.ArraySet):
            setter = target.expr.accept(self).value
            index = target.index.accept(self).value
            if type(index) == int:
                if abs(index) < len(setter):
                    index = index % len(setter)
                    setter[index] = value
                    return value
                self.error(operator, "Array index out of range.")
            self.error(operator, "Attempted to use a non-integer index.")
        elif isinstance(target, ast.Array):
            source = value.value
            if len(target.array) != len(source):
                self.error(
                    operator, "Attempted an assignment between two arrays of different sizes.")
            for n in range(len(source)):
                self.assign_search(env, target.array[n], operator, source[n])
            return value
        elif isinstance(target, ast.Map):
            res = {}
            source = value.value
            for key in target.map.keys():
                if key not in source:
                    self.error(
                        operator, f"Attempted to extract the unknown key '{key}' from the right-hand-side.")
                self.assign_search(env, target.map[key], operator, source[key])
                res[key] = source[key]
            return res
        self.error(operator, "Attempted to assign to a wrong target.")

    def assign(self, node: ast.Expr):
        # Capture environment, because expression might change it.
        previous = self.env
        value = node.expr.accept(self)
        return self.assign_search(previous, node.target, node.operator, value)

    def declaration(self, node: ast.Expr):
        # operator, identifier
        identifier = node.token.literal
        self.env.define(identifier)
        return MValue(None, None)

    def array(self, node: ast.Expr):
        previous = self.env
        values = []
        try:
            self.env = Environment(enclosing=self.env)
            self.env.define("this", MValue(values, None))
            for expr in node.array:
                value = expr.accept(self)
                values.append(value)
        finally:
            self.env = previous
        
        return MValue(values, None)

    def map(self, node: ast.Expr):
        previous = self.env
        values = {}
        try:
            self.env = Environment(enclosing=self.env)
            self.env.define("this", MValue(values, None))
            for key, expr in node.map.items():
                value = expr.accept(self)
                values[key] = value
        finally:
            self.env = previous
        return MValue(values, None)

    def block(self, node: ast.Expr):
        env = Environment(enclosing=self.env)
        return self.execute_block(node, env)

    def execute_block(self, block: ast.Block, env: Environment):
        # Save enclosing environment.
        previous = self.env
        value = None
        try:
            self.env = env
            for expr in block.exprs:
                value = expr.accept(self)
        finally:
            # Restore the enclosing environment, potentially discarding many nested inner ones.
            self.env = previous
        return value

    def conditional(self, node: ast.Expr):
        for n in range(len(node.conds)):
            condition = node.conds[n].accept(self).value
            if type(condition) != bool:
                self.error(
                    node.operators[n], "Condition must evaluate to a boolean value.")
            if condition:
                return node.exprs[n].accept(self)
        if node.default is not None:
            return node.default.accept(self)
        return MValue(None, None)

    def forloop(self, node: ast.Expr):
        value = None
        target = node.target
        iterator = node.iterator.accept(self).value
        if type(iterator) == list:
            env = Environment(enclosing=self.env)
            for iter in iterator:
                try:
                    self.assign_search(env, target, node.operator, iter)
                    value = self.execute_block(node.expr, env)
                except ast.Break as e:
                    value = e.expr
                    break
                except ast.Continue as e:
                    pass
        elif type(iterator) == dict:
            env = Environment(enclosing=self.env)
            for iter in iterator.items():
                iter = MValue([MValue(iter[0],None), iter[1]], None)
                try:
                    self.assign_search(env, target, node.operator, iter)
                    value = self.execute_block(node.expr, env)
                except ast.Break as e:
                    value = e.expr
                    break
                except ast.Continue as e:
                    pass
        elif isinstance(iterator, ast.Callable):
            env = Environment(enclosing=self.env)
            iter = iterator.call([])
            while iter.value is not None:
                try:
                    self.assign_search(env, target, node.operator, iter)
                    value = self.execute_block(node.expr, env)
                except ast.Break as e:
                    value = e.expr
                    break
                except ast.Continue as e:
                    pass
                iter = iterator.call([])
        else:
            self.error(node.operator,
                       "Can only iterate over array, object, or callable.")
        return value

    def call(self, node: ast.Expr):
        callee = node.expr.accept(self)
        args = []
        for argument in node.arguments:
            arg = argument.accept(self)
            args.append(arg)
        if isinstance(callee, MFunction):
            try:
                return callee.call(args)
            except ast.TypeError as e:
                self.error(node.operator, str(e))
                return MValue(None, None)

        # Calling a function on a constant value.
        if len(args) > 0:
            self.error(
                node.operator, "Attempted to call a constant function with one or more arguments.")
        return callee

    def function(self, node: ast.Expr):
        node.types = node.types.accept(self)
        if type(node.expr) == ast.Terminal and node.expr.token.ttype == ast.TokenType.MAGIC:
            magic_callable = MMagicFunction(ip=self, definition=node)
            return magic_callable
        try:
            user_callable = MUserFunction(ip=self, definition=node)
            # Create a new environment to protect the closure environment.
            self.env = Environment(enclosing=self.env)
        except Exception as e:
            print(e)
        return user_callable

    def type_definition(self, node: ast.Expr):
        operator = node.operator
        definition = node.expr.accept(self)
        # Create a new environment to protect the closure environment.
        self.env = Environment(enclosing=self.env)
        usertype = MType(ip=self, definition=definition)
        return usertype

    def type_annotation(self, node: ast.Expr):
        annotation = node.annotation.literal
        expr = node.expr.accept(self)
        expr.annotation = annotation
        return expr

    def type_grouping(self, node: ast.Expr):
        expr = node.expr.accept(self)
        return ast.TypeGrouping(expr=expr)

    def type_unary(self, node: ast.Expr):
        expr = node.expr.accept(self)
        operator = node.operator
        return ast.TypeUnary(operator=operator, expr=expr)

    def type_binary(self, node: ast.Expr):
        left = node.left.accept(self)
        right = node.right.accept(self)
        operator = node.operator
        return ast.TypeBinary(left=left, operator=operator, right=right)

    def type_terminal(self, node: ast.Expr):
        if node.token.ttype not in [ast.TokenType.ID, ast.TokenType.TYPE]:
            self.error(node.token, "Variable must be a type.")
        return node

    def type_array(self, node: ast.Expr):
        array = []
        for expr in node.array:
            new_node = expr.accept(self)
            array.append(new_node)
        return ast.TypeArray(array=array)

    def type_map(self, node: ast.Expr):
        dictionary = {}
        for key, expr in node.map.items():
            new_node = expr.accept(self)
            dictionary[key] = new_node
        return ast.TypeMap(map=dictionary)


