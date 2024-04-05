import re 
from scripting.ast import TokenType, Token, Expr, List, Dict

TABLEN = 4
MAXDEPTH = 5
LINELEN = 80

class Printer():

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

    def remaining_line_space(self):
        return LINELEN - self.indent * TABLEN
    
    def shorten(self, string):
        string = string.replace("\n", " ")
        string = re.sub(" +", " ", string)
        return string
    
    def shorten_if_possible(self, long):
        short = self.shorten(long)
        if len(short) < self.remaining_line_space():
            return short
        return long

    def is_max_depth(self):
        if self.indent >= MAXDEPTH:
            return True
        return False

    def program(self, node):
        content = ""
        exprs = node.program
        for expr in exprs:
            content += expr.accept(self) + "\n"
        return content

    def annotation(self, node):
        op = node.operator.literal
        comment = node.comment.literal
        expr = node.expr.accept(self)
        content = "\n" + self.prefix + f'{op} "{comment}"\n' + self.prefix + expr
        return self.shorten_if_possible(content) 

    def binary(self, node):
        left = node.left.accept(self)
        right = node.right.accept(self)
        op = node.operator.literal
        return f"{left} {op} {right}"

    def unary(self, node):
        op = node.operator.literal
        expr = node.expr.accept(self)
        if node.operator.ttype == TokenType.MINUS:
            return f"{op}{expr}"
        elif node.operator.ttype == TokenType.NOT:
            return f"{op} {expr}"
        elif node.operator.ttype == TokenType.QUESTION:
            return f"{expr}{op}"
        return f"{op} {expr}" # Should be "return", "break", "continue"

    def grouping(self, node):
        if self.is_max_depth(): return "..."
        expr = node.expr.accept(self)
        return f"({expr})"

    def terminal(self, node):
        literal = node.token.literal
        if node.token.ttype == TokenType.NULL:
            literal = "null"
        if node.token.ttype == TokenType.BOOLEAN:
            literal = "true" if literal else "false"
        if node.token.ttype == TokenType.STRING:
            literal = f"\"{literal}\""
        if node.token.ttype == TokenType.INTEGER:
            literal = str(literal)
        if node.token.ttype == TokenType.NUMBER:
            literal = str(literal)
        return literal

    def get(self, node):
        # expr, index
        expr = node.expr.accept(self)
        index = node.index
        if index.ttype == TokenType.INTEGER:
            return f"{expr}[{index.literal}]"
        elif index.ttype == TokenType.ID:
            return f"{expr}.{index.literal}"

    def set(self, node):
        return self.get(self, node)

    def assign(self, node):
        expr = node.expr.accept(self)
        target = node.target.accept(self)
        return f"{target} = {expr}"

    def declaration(self, node):
        # operator, identifier
        identifier = node.token.literal
        return f"def {identifier}"

    def array(self, node):
        self.indent_incr()
        items = []
        for expr in node.array:
            txt = self.prefix + expr.accept(self)
            items.append(txt)
        self.indent_decr()
        content = "[\n" + ",\n".join(items) + "\n" + self.prefix + "]"
        return self.shorten_if_possible(content)

    def map(self, node):
        self.indent_incr()
        content = "{\n"
        for key, expr in node.map.items():
            content += self.prefix + key + ": " + expr.accept(self) + ",\n"
        self.indent_decr()
        content += self.prefix + "}"
        return self.shorten_if_possible(content)

    def block(self, node):
        self.indent_incr()
        content = "do {\n"
        for expr in node.exprs:
            content += self.prefix + expr.accept(self) + "\n"
        self.indent_decr()
        content += self.prefix + "}"
        return self.shorten_if_possible(content)

    def conditional(self, node):
        cond = node.conds[0].accept(self)
        expr = node.exprs[0].accept(self)
        content = "if " + cond + " " + expr
        for n in range(1, len(node.conds)):
            cond = node.conds[n].accept(self)
            expr = node.exprs[n].accept(self)
            content += "\n" + self.prefix + "elif " + cond + " " + expr
        if node.default is not None:
            expr = node.default.accept(self)
            content += "\n" + self.prefix + "else " + expr
        return self.shorten_if_possible(content)

    def whileloop(self, node):
        cond = node.cond.accept(self)
        expr = node.expr.accept(self)
        content = f"while {cond} {expr}"
        return self.shorten_if_possible(content)

    def call(self, node):
        callee = node.expr.accept(self)
        args = "("
        if len(node.arguments) > 0:
            args += node.arguments[0].accept(self)
            for argument in node.arguments[1:]:
                args += ", " + argument.accept(self)
        args += ")"
        return callee + args

    def function(self, node):
        expr = node.expr.accept(self)
        pairs = []
        for param, param_type in zip(node.parameters, node.param_types):
            name = param.literal
            type_spec = param_type.accept(self)
            pairs.append(f"{name}: {type_spec}")
        parameters = ", ".join(pairs)
        out_spec = node.out_type.accept(self)
        return f"function({parameters}) -> {out_spec} {expr}"

    def type_binary(self, node):
        left = node.left.accept(self)
        op = node.operator.literal
        right = node.right.accept(self)
        return f"{left} {op} {right}"

    def print_value(self, value):
        repr = None
        if value is None:
            repr = "null"
        elif type(value) == str:
            repr = f'"{value}"'
        elif type(value) == float or type(value) == int:
            repr = str(value)
        elif type(value) == bool:
            repr = "true" if value else "false"
        elif type(value) == list:
            items = []
            self.indent_incr()
            for item in value:
                txt = self.prefix + self.print_value(item)
                items.append(txt)
            self.indent_decr()
            repr = "[\n" + ",\n".join(items) + "\n" + self.prefix + "]"
        elif type(value) == dict:
            items = []
            self.indent_incr()
            for key, item in value.items():
                txt = self.prefix + f'"{key}"' + ": " + self.print_value(item)
                items.append(txt)
            self.indent_decr()
            repr = "{\n" + ",\n".join(items) + "\n" + self.prefix + "}"
        else:
            repr = str(value)
        return self.shorten_if_possible(repr)

    def print(self, value):
        if isinstance(value, Expr):
            return value.accept(self)
        return self.print_value(value)            
