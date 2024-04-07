from typing import Optional, Any, List
from abc import abstractmethod
import ms.ast as ast
from ms.printer import Printer
from ms.parser import Parser


class Environment():

    def __init__(self, enclosing=None):
        self.enclosing: Optional['Environment'] = enclosing
        self.vars = {}

    def define(self, key: str, value: Any = None) -> bool:
        self.vars[key] = value
        return True

    def set(self, key: str, value: Any) -> bool:
        if key in self.vars:
            self.vars[key] = value
            return True
        if self.enclosing is not None:
            return self.enclosing.set(key, value)
        raise KeyError()

    def get(self, key: str) -> Any:
        if key in self.vars:
            return self.vars[key]
        if self.enclosing is not None:
            return self.enclosing.get(key)
        raise KeyError()







class Interpreter:

    def __init__(self, interactive=False):
        self.printer = Printer()
        self.parser = Parser(interactive=interactive)
        self.reset()

    def reset(self):
        self.parser.reset()
        self.env = Environment()

    def eval(self, instr: str):
        val = None
        tree = self.parser.parse(instr)
        if tree is None:
            return val
        try:
            val = tree.accept(self)
        except ast.Return as e:
            print(f"I'm here! {e}")
            if e.operator.ttype in [ast.TokenType.BREAK, ast.TokenType.CONTINUE]:
                self.parser.lexer.report_error(
                    e.operator.line, 
                    e.operator.col,
                    "RUNTIME ERROR",
                    f"Unexpected control flow expression '{e.operator.literal}'.")
            else:
                return e.expr
        except Exception as e:
            # print("RUNTIME ERROR (!): " + str(e))
            # raise e
            pass
        return val

    def define(self, name: str, value: Any):
        self.env.define(name, value)

    def error(self, token: ast.Token, msg):
        self.parser.lexer.report_error(
            token.line, token.col, "RUNTIME ERROR", msg)
        raise Exception(msg)

    def program(self, node):
        value = None
        exprs = node.program
        for expr in exprs:
            value = expr.accept(self)
        return value

    def annotation(self, node):
        operator = node.operator
        comment = node.comment.literal
        value = node.expr.accept(self)
        print(f"\033[32m{comment}\033[0m")
        return value

    def binary(self, node):

        operator = node.operator

        # Short-circuit operators.
        if operator.ttype == ast.TokenType.OR:
            lvalue = node.left.accept(self)
            if type(lvalue) != bool:
                self.error(operator, "Operands must be boolean.")
            if lvalue:
                return True
            rvalue = node.right.accept(self)
            if type(rvalue) == bool:
                return rvalue
            self.error(operator, "Operands must be boolean.")

        if operator.ttype == ast.TokenType.AND:
            lvalue = node.left.accept(self)
            if type(lvalue) != bool:
                self.error(operator, "Operands must be boolean.")
            if not lvalue:
                return False
            rvalue = node.right.accept(self)
            if type(rvalue) == bool:
                return rvalue
            self.error(operator, "Operands must be boolean.")

        # Standard operators.
        lvalue = node.left.accept(self)
        rvalue = node.right.accept(self)

        if ((type(lvalue) == int or type(lvalue) == float)
                and (type(rvalue) == int or type(rvalue) == float)):

            if operator.ttype == ast.TokenType.PLUS:
                return lvalue + rvalue
            elif operator.ttype == ast.TokenType.MINUS:
                return lvalue - rvalue
            elif operator.ttype == ast.TokenType.MULT:
                return lvalue * rvalue
            elif operator.ttype == ast.TokenType.DIV:
                return lvalue / rvalue
            elif operator.ttype == ast.TokenType.MOD:
                return lvalue % rvalue
            elif operator.ttype == ast.TokenType.GREATER:
                return lvalue < rvalue
            elif operator.ttype == ast.TokenType.GREATER_EQ:
                return lvalue <= rvalue
            elif operator.ttype == ast.TokenType.LESS:
                return lvalue < rvalue
            elif operator.ttype == ast.TokenType.LESS_EQ:
                return lvalue <= rvalue
            elif operator.ttype == ast.TokenType.EQ:
                return lvalue == rvalue
            elif operator.ttype == ast.TokenType.NEQ:
                return lvalue != rvalue
            self.error(
                operator, "Unexpected operator for integer/number operands.")

        elif type(lvalue) == bool and type(rvalue) == bool:
            if operator.ttype == ast.TokenType.EQ:
                return lvalue == rvalue
            elif operator.ttype == ast.TokenType.NEQ:
                return lvalue != rvalue
            self.error(operator, "Unexpected operator for boolean operands.")

        elif type(rvalue) == str and type(lvalue) == str:
            if operator.ttype == ast.TokenType.PLUS:
                return lvalue + rvalue
            elif operator.ttype == ast.TokenType.GREATER:
                return lvalue > rvalue
            elif operator.ttype == ast.TokenType.GREATER_EQ:
                return lvalue >= rvalue
            elif operator.ttype == ast.TokenType.LESS:
                return lvalue < rvalue
            elif operator.ttype == ast.TokenType.LESS_EQ:
                return lvalue <= rvalue
            elif operator.ttype == ast.TokenType.EQ:
                return lvalue == rvalue
            elif operator.ttype == ast.TokenType.NEQ:
                return lvalue != rvalue
            self.error(operator, "Unexpected operator for string operands.")

        elif type(rvalue) == UserType and type(lvalue) == UserType:
            if operator.ttype == ast.TokenType.ARROW:
                value = UserType(
                    self,
                    ast.Binary(
                        left=lvalue.definition,
                        operator=operator,
                        right=rvalue.definition
                    )
                )
                return value

        self.error(operator, "Inconsistent operands.")

    def unary(self, node):
        operator = node.operator
        expr = node.expr.accept(self)
        if operator.ttype == ast.TokenType.NOT:
            if type(expr) == bool:
                return not expr
            self.error(operator, "Expected a boolean.")
        elif operator.ttype == ast.TokenType.MINUS:
            if type(expr) == int or type(expr) == float:
                return -expr
            self.error(operator, "Expected a number.")
        elif operator.ttype in [ast.TokenType.RETURN, ast.TokenType.BREAK, ast.TokenType.CONTINUE]:
            raise ast.Return(operator, expr)
        elif operator.ttype == ast.TokenType.QUESTION:
            if type(expr) == UserType:
                value = UserType(self, ast.Unary(
                    operator=operator, expr=expr.definition))
                return value
            self.error(operator, "Expected a preceding type.")
        self.error(operator, "Wrong unary operation.")

    def grouping(self, node):
        expr = node.expr.accept(self)
        return expr

    def terminal(self, node):
        if node.token.ttype == ast.TokenType.ID:
            identifier = node.token.literal
            try:
                return self.env.get(identifier)
            except KeyError:
                self.error(node.token, "Undefined variable.")
        if node.token.ttype == ast.TokenType.TYPE:
            return UserType(self, node)
        return node.token.literal

    def get(self, node):
        # expr, index
        operator = node.operator
        getter = node.expr.accept(self)
        index = node.index.accept(self)
        if type(getter) == list:
            if type(index) == int:
                if abs(index) < len(getter):
                    index = index % len(getter)
                    return getter[index]
                self.error(operator, "Array index out of range.")
            self.error(operator, "Array index must be an integer.")
        if type(getter) == dict and type(index) == str:
            if index in getter:
                return getter[index]
            self.error(operator, f"Unknown property '{index}'.")
        self.error(operator, "Wrong property access.")

    def set(self, node):
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
        elif isinstance(target, ast.Declaration):
            # Capture inner declaration!
            identifier = target.token.literal
            env.define(identifier, value)
            return value
        elif isinstance(target, ast.Set):
            setter = target.expr.accept(self)
            index = target.index.accept(self)
            if type(setter) == dict and type(index) == str:
                if index in setter:
                    setter[index] = value
                    return value
                self.error(
                    operator, "Attempted to assign to an unknown property.")
            elif type(setter) == list:
                if type(index) == int:
                    if abs(index) < len(setter):
                        index = index % len(setter)
                        setter[index] = value
                        return value
                    self.error(operator, "Array index out of range.")
                self.error(
                    operator, "Attempted to use a non-integer index.")
        elif isinstance(target, ast.Array):
            if len(target.array) != len(value):
                self.error(
                    operator, "Attempted an assignment between two arrays of different sizes.")
            for n in range(len(value)):
                self.assign_search(env, target.array[n], operator, value[n])
            return value
        elif isinstance(target, ast.Map):
            res = {}
            for key in target.map.keys():
                if key not in value:
                    self.error(
                        operator, f"Attempted to extract the unknown key '{key}' from the right-hand-side.")
                self.assign_search(env, target.map[key], operator, value[key])
                res[key] = value[key]
            return res
        self.error(operator, "Attempted to assign to a wrong target.")

    def assign(self, node):
        # Capture environment, because expression might change it.
        previous = self.env
        value = node.expr.accept(self)

        return self.assign_search(previous, node.target, node.operator, value)

    def declaration(self, node):
        # operator, identifier
        identifier = node.token.literal
        self.env.define(identifier)
        return None

    def array(self, node):
        values = []
        for expr in node.array:
            value = expr.accept(self)
            values.append(value)
        return values

    def map(self, node):
        previous = self.env
        values = {}
        try:
            self.env = Environment(enclosing=self.env)
            self.env.define("this", values)
            for key, expr in node.map.items():
                value = expr.accept(self)
                values[key] = value
        finally:
            self.env = previous
        return values

    def block(self, node):
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

    def conditional(self, node):
        for n in range(len(node.conds)):
            condition = node.conds[n].accept(self)
            if type(condition) != bool:
                self.error(
                    node.operators[n], "Condition must evaluate to a boolean value.")
            if condition:
                return node.exprs[n].accept(self)
        if node.default is not None:
            return node.default.accept(self)
        return None

    def whileloop(self, node):
        cond = node.cond.accept(self)
        if type(cond) != bool:
            self.error(node.operator,
                       "Condition must evaluate to a boolean value.")
        while cond:
            try:
                value = node.expr.accept(self)
            except ast.Return as e:
                if e.operator.ttype == ast.TokenType.BREAK:
                    value = e.expr
                    break
                elif e.operator.ttype == ast.TokenType.CONTINUE:
                    value = e.expr
                    pass
                elif e.operator.ttype == ast.TokenType.RETURN:
                    raise e
            cond = node.cond.accept(self)
            if type(cond) != bool:
                self.error(node.operator,
                           "Condition must evaluate to a boolean value.")
        return value

    def forloop(self, node):
        value = None
        target = node.target
        iterator = node.iterator.accept(self)
        if type(iterator) == list:
            print("Iterate over array.")
            env = Environment(enclosing=self.env)
            for iter in iterator:
                try:
                    self.assign_search(env, target, node.operator, iter)
                    value = self.execute_block(node.expr, env)
                except ast.Return as e:
                    if e.operator.ttype == ast.TokenType.BREAK:
                        value = e.expr
                        break
                    elif e.operator.ttype == ast.TokenType.CONTINUE:
                        pass
                    elif e.operator.ttype == ast.TokenType.RETURN:
                        raise e
        elif type(iterator) == dict:
            print("Iterate over object.")
            env = Environment(enclosing=self.env)
            for iter in iterator.items():
                self.assign_search(env, target, node.operator, iter)
                value = self.execute_block(node.expr, env)
        elif isinstance(iterator, Callable):
            print("Iterate over callable.")
            env = Environment(enclosing=self.env)
            iter = iterator.call([])
            while iter is not None:
                print(f"iter = {iter}")
                try:
                    self.assign_search(env, target, node.operator, iter)
                except Exception as e:
                    print("captured!")
                    print(e)
                print(f"after assign search...")
                value = self.execute_block(node.expr, env)
                print(f"value = {value}")
                iter = iterator.call([])
        else:
            self.error(node.operator, "Can only iterate over array, object, or callable.")
        return value
        

    def call(self, node):
        callee = node.expr.accept(self)
        args = []
        for argument in node.arguments:
            arg = argument.accept(self)
            args.append(arg)
        if isinstance(callee, Callable):
            try:
                callee
                return callee.call(args)
            except ast.Return as e:
                if e.operator.ttype == ast.TokenType.RETURN:
                    return e.expr
                raise e
        if len(args) > 0:
            self.error(
                node.operator, "Attempted to call a constant function with one or more arguments.")
        return callee

    def function(self, node):
        # Current environment is the closure environment for the function.
        user_callable = UserCallable(ip=self, env=self.env, function=node)
        # Create a new environment to protect the closure environment.
        self.env = Environment(enclosing=self.env)
        return user_callable


# Types.

class UserType():
    def __init__(self, ip: Interpreter, definition: ast.Expr):
        self.ip = ip
        self.definition = definition

    def __expr__(self):
        text = self.ip.printer.print(self.definition)
        return text

    def __str__(self):
        text = self.ip.printer.print(self.definition)
        return text


# Callables.


class Callable():
    def call(self, ip: Interpreter, args: List[Any]) -> Any:
        pass


class UserCallable(Callable):
    env: Environment
    function: ast.Function

    def __init__(self, ip: Interpreter, env: Environment = None, function: ast.Function = None):
        self.ip = ip
        self.env = env
        self.function = function

    def call(self, args: List[Any]) -> Any:
        # Call function with new environment containing arguments.
        env = Environment(enclosing=self.env)
        for parameter, arg in zip(self.function.parameters, args):
            env.define(parameter.literal, arg)
        value = self.ip.execute_block(self.function.expr, env)
        return value

    def __repr__(self):
        return self.ip.printer.print(self.function)

    def __str__(self):
        return self.ip.printer.print(self.function)


# Native functions.

class NativeCallable(Callable):
    def __init__(self, ip: Interpreter, env: Environment = None, function: ast.Function = None):
        self.ip = ip
        self.env = env
        self.function = function

    @abstractmethod
    def call(self, args: List[Any]) -> Any:
        pass

    def __repr__(self):
        return "<native function>"

    def __str__(self):
        return "<native function>"
