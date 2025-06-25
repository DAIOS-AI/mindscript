from typing import Optional, Any, List, Callable
import mindscript.ast as ast
from mindscript.printer import Printer
from mindscript.parser import Parser
from mindscript.types import TypeChecker
from mindscript.objects import MObject, MValue, MType, MFunction
from mindscript.oracle import MOracleFunction


# Environment.

class Environment():

    def __init__(self, enclosing=None):
        self.enclosing: Optional['Environment'] = enclosing
        self.vars = {}

    def define(self, key: str, value: MValue = None) -> bool:
        if value is None:
            value = MValue(None, None)
        self.vars[key] = value
        return True

    def set(self, key: str, value: MValue) -> bool:
        if key in self.vars:
            self.vars[key] = value
            return True
        if self.enclosing is not None:
            return self.enclosing.set(key, value)
        raise KeyError()

    def get(self, key: str) -> MObject:
        if key in self.vars:
            return self.vars[key]
        if self.enclosing is not None:
            return self.enclosing.get(key)
        raise KeyError()


# User-defined functions.

class MUserFunction(MFunction):

    def __init__(self, ip: 'Interpreter', definition: ast.Function):  # type: ignore
        super().__init__(ip, definition)

    def func(self, args: List[MObject]) -> MObject:
        env = Environment(enclosing=self.environment)
        for param, arg in zip(self.params, args):
            env.define(param.literal, arg)
        try:
            value = self.interpreter.execute_block(self.definition.expr, env)
        except ast.Return as e:
            value = e.expr
        return value


# Interpreter.

class Interpreter:

    def __init__(self, interactive=False, backend=None):
        self.printer = Printer()
        self.parser = Parser(interactive=interactive)
        self.checker = TypeChecker(self)
        if backend is None:
            raise ValueError("The interpreter must be started with an oracle backend.")
        self.backend = backend
        self.buffer = "<interpreter>"
        self.reset()

    def reset(self):
        self.parser.reset()
        self.env = Environment()

    def set_buffer(self, buffer: str):
        self.parser.lexer.set_stream(buffer)
        self.buffer = buffer

    def eval(self, instr: str, buffer: str = None):
        if buffer is None:
            buffer = self.buffer
        self.buffer = buffer
        val = MValue(None, None)
        tree = self.parser.parse(instr, buffer)
        if tree is None:
            return val
        try:
            val = tree.accept(self)
        except (ast.Break, ast.Continue) as e:
            self.error
            self.parser.lexer.report_error(
                e.operator.buffer, 
                e.operator.index,
                "RUNTIME ERROR",
                f"Unexpected control flow expression '{e.operator.literal}'"
            )
        except ast.RuntimeError as e:
            pass
            
        return val

    def typeof(self, value: MObject) -> MType:
        definition = self.checker.typeof(value)
        return MType(self, definition)

    def issubtype(self, subtype: MObject, supertype: MObject) -> bool:
        res = self.checker.issubtype(subtype, supertype)
        return res

    def checktype(self, value: MObject, required: MType) -> bool:
        return self.checker.checktype(value, required)

    def define(self, name: str, value: MObject):
        self.env.define(name, value)

    def print(self, value: MObject):
        return self.printer.print(value)

    def error(self, token: ast.Token, msg):
        self.parser.lexer.report_error(
            token.buffer, token.index, "RUNTIME ERROR", msg)
        raise ast.RuntimeError(msg)

    def exit(self):
        raise ast.Exit()

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

    def compare(self, lvalue: MObject, rvalue: MObject):
        if type(lvalue) == MValue and type(rvalue) == MValue:
            x = lvalue.value
            y = rvalue.value
            if x is None and y is None:
                return True
            elif type(x) == bool and type(y) == bool:
                return x == y
            elif (type(x) == int or type(x) == float) and (type(y) == int or type(y) == float):
                return x == y
            elif type(x) == str and type(y) == str: 
                return x == y
            elif type(x) == list and type(y) == list:
                if len(x) == len(y):
                    return all(self.compare(subx, suby) for subx, suby in zip(x, y))
                else:
                    return False
            elif type(x) == dict and type(y) == dict:
                if len(x) == len(y):
                    return all(self.compare(x[key], y[key]) for key in x.keys())
                else:
                    return False
        elif type(lvalue) == MType and type(lvalue) == MType:
            return self.issubtype(lvalue, rvalue) and self.issubtype(rvalue, lvalue)
        elif isinstance(lvalue, MFunction) and isinstance(rvalue, MFunction):
            return id(lvalue) == id(rvalue)
        return False

    def binary(self, node: ast.Expr):

        operator = node.operator

        # Short-circuit operators.
        if operator.ttype == ast.TokenType.OR:
            lexpr = node.left.accept(self)
            if type(lexpr) != MValue or type(lexpr.value) != bool:
                self.error(operator, "Operands must be boolean.")
            if lexpr.value:
                return MValue(True, None)
            rexpr = node.right.accept(self)
            if type(rexpr) == MValue and type(rexpr.value) == bool:
                return MValue(rexpr.value, None)
            self.error(operator, "Operands must be boolean.")

        if operator.ttype == ast.TokenType.AND:
            lexpr = node.left.accept(self)
            if type(lexpr) != MValue or type(lexpr.value) != bool:
                self.error(operator, "Operands must be boolean.")
            if not lexpr.value:
                return MValue(False, None)
            rexpr = node.right.accept(self)
            if type(rexpr) == MValue and type(rexpr.value) == bool:
                return MValue(rexpr.value, None)
            self.error(operator, "Operands must be boolean.")

        # Standard operators.
        lexpr = node.left.accept(self)
        rexpr = node.right.accept(self)

        if operator.ttype == ast.TokenType.EQ:
            return MValue(self.compare(lexpr, rexpr), None)
        if operator.ttype == ast.TokenType.NEQ:
            return MValue(not self.compare(lexpr, rexpr), None)

        if type(lexpr) != MValue or type(rexpr) != MValue:
            self.error(operator, "Wrong operand types.")

        lvalue = lexpr.value
        rvalue = rexpr.value

        if (type(lvalue) == int and type(rvalue) == int):
            if operator.ttype == ast.TokenType.PLUS:
                return MValue(int(lvalue + rvalue), None)
            elif operator.ttype == ast.TokenType.MINUS:
                return MValue(int(lvalue - rvalue), None)
            elif operator.ttype == ast.TokenType.MULT:
                return MValue(int(lvalue * rvalue), None)
            elif operator.ttype == ast.TokenType.DIV:
                if rvalue == 0:
                    self.error(operator, "Division by zero.")
                return MValue(int(lvalue / rvalue), None)
            elif operator.ttype == ast.TokenType.MOD:
                return MValue(int(lvalue % rvalue), None)
            elif operator.ttype == ast.TokenType.GREATER:
                return MValue(lvalue > rvalue, None)
            elif operator.ttype == ast.TokenType.GREATER_EQ:
                return MValue(lvalue >= rvalue, None)
            elif operator.ttype == ast.TokenType.LESS:
                return MValue(lvalue < rvalue, None)
            elif operator.ttype == ast.TokenType.LESS_EQ:
                return MValue(lvalue <= rvalue, None)
            self.error(
                operator, "Unexpected operator for integer/number operands.")

        if ((type(lvalue) == int or type(lvalue) == float)
                and (type(rvalue) == int or type(rvalue) == float)):
            if operator.ttype == ast.TokenType.PLUS:
                return MValue(lvalue + rvalue, None)
            elif operator.ttype == ast.TokenType.MINUS:
                return MValue(lvalue - rvalue, None)
            elif operator.ttype == ast.TokenType.MULT:
                return MValue(lvalue * rvalue, None)
            elif operator.ttype == ast.TokenType.DIV:
                if rvalue == 0.0:
                    self.error(operator, "Division by zero.")
                return MValue(lvalue / rvalue, None)
            elif operator.ttype == ast.TokenType.MOD:
                return MValue(lvalue % rvalue, None)
            elif operator.ttype == ast.TokenType.GREATER:
                return MValue(lvalue > rvalue, None)
            elif operator.ttype == ast.TokenType.GREATER_EQ:
                return MValue(lvalue >= rvalue, None)
            elif operator.ttype == ast.TokenType.LESS:
                return MValue(lvalue < rvalue, None)
            elif operator.ttype == ast.TokenType.LESS_EQ:
                return MValue(lvalue <= rvalue, None)
            self.error(
                operator, "Unexpected operator for integer/number operands.")

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
            self.error(operator, "Unexpected operator for string operands.")
        
        elif type(lvalue) == list and type(rvalue) == list:
            if operator.ttype == ast.TokenType.PLUS:
                return MValue(lvalue + rvalue, None)

        elif type(lvalue) == dict and type(rvalue) == dict:
            if operator.ttype == ast.TokenType.PLUS:
                return MValue(lvalue | rvalue, None)
            
        self.error(operator, "Wrong operand types.")

    def unary(self, node: ast.Expr):
        operator = node.operator
        expr = node.expr.accept(self)
        if operator.ttype == ast.TokenType.NOT:
            if type(expr) == MValue and type(expr.value) == bool:
                return MValue(not expr.value, None)
            self.error(operator, "Expected a boolean.")
        elif operator.ttype == ast.TokenType.MINUS:
            if type(expr) == MValue and type(expr.value) == int or type(expr.value) == float:
                return MValue(-expr.value, None)
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
        getter_expr = node.expr.accept(self)
        index_expr = node.index.accept(self)

        if type(getter_expr) != MValue:
            self.error(operator, "Attempted to access a member on a non-array.")
        if type(index_expr) != MValue:
            self.error(operator, "Array index must be an integer.")

        getter = getter_expr.value
        index = index_expr.value

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
        getter_expr = node.expr.accept(self)
        index_expr = node.index.accept(self)

        if type(getter_expr) != MValue:
            self.error(operator, "Attempted to access a property on a non-object.")
        if type(index_expr) != MValue:
            self.error(operator, "Wrong object property.")

        getter = getter_expr.value
        index = index_expr.value

        if type(getter) == dict and type(index) == str:
            if index in getter:
                return getter[index]
            self.error(operator, f"Unknown property '{index}'.")
        self.error(operator, "Attempted to access a property on a non-object.")

    def set(self, node: ast.Expr):
        # This should never be called directly.
        self.error(node.index, "Set should not be interpreted directly.")

    def destructure(self, env, target, operator, value, define=False):
        if isinstance(target, ast.Terminal):
            identifier = target.token.literal
            try:
                if define: env.define(identifier)
                env.set(identifier, value)
            except KeyError:
                self.error(
                    operator, "Attempted to assign to an uninitialized variable.")
            return value
        elif isinstance(target, ast.Annotation):
            # Push the annotation into the value!
            annotation = target.annotation.literal
            value.annotation = annotation
            return self.destructure(env, target.expr, operator, value, define)
        elif isinstance(target, ast.Declaration):
            # Capture inner declaration!
            identifier = target.token.literal
            env.define(identifier, value)
            return value
        elif isinstance(target, ast.ObjectSet):
            setter_expr = target.expr.accept(self)
            index_expr = target.index.accept(self)

            if type(setter_expr) != MValue:
                self.error(operator, "Attempted to assign to a non-object.")
            if type(index_expr) != MValue:
                self.error(operator, "Wrong object property.")
            setter = setter_expr.value
            index = index_expr.value

            if type(index) == str:
                setter[index] = value
                return value
        elif isinstance(target, ast.ArraySet):
            setter_expr = target.expr.accept(self)
            index_expr = target.index.accept(self)

            if type(setter_expr) != MValue:
                self.error(operator, "Attempted to assign to member of a non-array.")
            if type(index_expr) != MValue:
                self.error(operator, "Attempted to use a non-interger index.")
            setter = setter_expr.value
            index = index_expr.value

            if type(index) == int:
                if abs(index) < len(setter):
                    index = index % len(setter)
                    setter[index] = value
                    return value
                self.error(operator, "Array index out of range.")
            self.error(operator, "Attempted to use a non-integer index.")
        elif type(target) == ast.Array and type(value.value) == list:
            res = []
            source = value.value
            if len(target.array) > len(source):
                self.error(
                    operator, "The assignment expects a larger array on the right-hand-side.")
            for n in range(len(target.array)):
                self.destructure(env, target.array[n], operator, source[n], define)
                res.append(source[n])
            return MValue(res, None)
        elif type(target) == ast.Map and type(value.value) == dict:
            res = {}
            source = value.value
            for key in target.map.keys():
                if key not in source:
                    self.error(
                        operator, f"Attempted to extract the unknown key '{key}' from the right-hand-side.")
                self.destructure(env, target.map[key], operator, source[key], define)
                res[key] = source[key]
            return MValue(res, None)
        self.error(operator, "Attempted to assign to a wrong target.")

    def assign(self, node: ast.Expr):
        # Capture environment, because expression on the rhs might change it,
        # e.g. in a function or type instantiation.
        previous = self.env
        value = node.expr.accept(self)
        return self.destructure(previous, node.target, node.operator, value)

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
            # Restore the enclosing environment, potentially 
            # discarding nested inner environment.
            self.env = previous
        return value

    def conditional(self, node: ast.Expr):
        for n in range(len(node.conds)):
            condexpr = node.conds[n].accept(self)
            if type(condexpr) != MValue:
                self.error(node.operators[n], "Condition must evaluate to a boolean value.")
            condition = condexpr.value
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
        iterator = node.iterator.accept(self)
        if isinstance(iterator, MFunction):
            env = Environment(enclosing=self.env)
            iter = iterator.call(node.operator, [MValue(None, None)])
            while type(iter) != MValue or iter.value is not None:
                try:
                    self.destructure(env, target, node.operator, iter, define=True)
                    value = self.execute_block(node.expr, env)
                except ast.Break as e:
                    value = e.expr
                    break
                except ast.Continue as e:
                    pass
                iter = iterator.call(node.operator, [MValue(None, None)])
        else:
            self.error(node.operator,
                       "Can only iterate over an iterator function.")
        return value

    def call(self, node: ast.Expr):
        callee = node.expr.accept(self)
        args = [arg.accept(self) for arg in node.arguments]
        if isinstance(callee, MFunction):
            return callee.call(node.operator, args)

        # Calling a function on a constant value.
        self.error(node.operator, "Not a function.")

    def function(self, node: ast.Expr):
        node.types = node.types.accept(self)
        try:
            if node.operator.ttype == ast.TokenType.FUNCTION:
                callable = MUserFunction(ip=self, definition=node)
            else:
                examples = node.expr.accept(self)
                callable = MOracleFunction(ip=self, definition=node, examples=examples)
            # Create a new environment to protect the closure environment.
            self.env = Environment(enclosing=self.env)
        except Exception as e:
            return MValue(None, None)
        return callable

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
        if (isinstance(expr, ast.TypeTerminal) 
            and expr.token.ttype == ast.TokenType.TYPE 
            and expr.token.literal == "Any"):
            return expr
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

    def type_enum(self, node: ast.Expr):
        values = node.expr.accept(self)
        if type(values) != MValue or type(values.value) != list or len(values.value) == 0:
            self.error(node.operator, "Expected a non-empty array of possible values.")
        return ast.TypeEnum(operator=node.operator, expr=node.expr, values=values)

    def type_array(self, node: ast.Expr):
        expr = node.expr.accept(self)
        return ast.TypeArray(expr=expr)

    def type_map(self, node: ast.Expr):
        dictionary = {}
        for key, expr in node.map.items():
            new_node = expr.accept(self)
            dictionary[key] = new_node
        return ast.TypeMap(map=dictionary, required=node.required)
