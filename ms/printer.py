import re 
from ms.ast import TokenType, Token, Expr, List, Dict, Terminal, Callable, UserType, Value

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
        comment = node.comment.literal
        expr = node.expr.accept(self)
        content = f"\n{self.prefix}# \"{comment}\"\n{self.prefix}{expr}\n"
        return content

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
        return f"{op}({expr})" # Should be "return", "break", "continue"

    def grouping(self, node):
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

    def array_get(self, node):
        expr = node.expr.accept(self)
        index = node.index.accept(self)
        return f"{expr}[{index}]"

    def object_get(self, node):
        expr = node.expr.accept(self)
        index = node.index.accept(self)
        return f"{expr}.{index}"

    def set(self, node):
        return self.get(self, node)

    def assign(self, node):
        expr = node.expr.accept(self)
        target = node.target.accept(self)
        return f"{target} = {expr}"

    def declaration(self, node):
        # operator, identifier
        identifier = node.token.literal
        return f"let {identifier}"

    def array(self, node):
        self.indent_incr()
        items = []
        for expr in node.array:
            txt = self.prefix + expr.accept(self)
            items.append(txt)
        self.indent_decr()
        return "[\n" + ",\n".join(items) + "\n" + self.prefix + "]"

    def map(self, node):
        self.indent_incr()
        items = []
        for key, expr in node.map.items():
            txt = self.prefix + key + ": " + expr.accept(self)
            items.append(txt)
        self.indent_decr()
        return "{\n" + ",\n".join(items) + "\n" + self.prefix + "}"

    def print_chunk(self, node):
        self.indent_incr()
        content = ""
        for expr in node.exprs:
            content += self.prefix + expr.accept(self) + "\n"
        self.indent_decr()
        return f"{content}"

    def block(self, node):
        content = "do\n"
        content += self.print_chunk(node) 
        content += self.prefix + "end"
        return content

    def conditional(self, node):
        cond = node.conds[0].accept(self)
        expr = node.exprs[0]
        content = "if " + cond + " then\n" + self.print_chunk(expr)
        for n in range(1, len(node.conds)):
            cond = node.conds[n].accept(self)
            expr = node.exprs[n]
            content += self.prefix + "elif " + cond + " then\n" + self.print_chunk(expr)
        if node.default is not None:
            expr = node.default
            content += self.prefix + "else\n" + self.print_chunk(expr)
        content += self.prefix + "end"
        return content

    def whileloop(self, node):
        cond = node.cond.accept(self)
        expr = node.expr.accept(self)
        content = f"while {cond} {expr}"
        return content

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
        pairs = []
        for param, param_type in zip(node.parameters, node.param_types):
            name = param.literal
            type_spec = param_type.accept(self)
            pairs.append(f"{name}: {type_spec}")
        parameters = ", ".join(pairs)
        out_spec = node.out_type.accept(self)
        expr = node.expr.accept(self)
        return f"function({parameters}) -> {out_spec} {expr}"

    def type_definition(self, node):
        expr = node.expr.accept(self)
        content = f"type {expr}"
        return content

    def type_annotation(self, node):
        comment = node.comment.literal
        expr = node.expr.accept(self)
        content = f"\n{self.prefix}# \"{comment}\"\n{self.prefix}{expr}\n"
        return content

    def type_terminal(self, node):
        return node.token.literal

    def type_unary(self, node):
        expr = node.expr.accept(self)
        return f"{expr}?"
    
    def type_binary(self, node):
        self.indent_incr()
        left = node.left.accept(self)
        right = node.right.accept(self)
        content = left + "\n"
        content += self.prefix + " -> " + right + "\n"
        self.indent_decr()
        return self.shorten_if_possible(content)
    
    def type_array(self, node):
        self.indent_incr()
        items = []
        for expr in node.array:
            txt = self.prefix + expr.accept(self)
            items.append(txt)
        self.indent_decr()
        return "[\n" + ",\n".join(items) + "\n" + self.prefix + "]"

    def type_map(self, node):
        self.indent_incr()
        items = []
        for key, expr in node.map.items():
            txt = self.prefix + key + ": " + expr.accept(self)
            items.append(txt)
        self.indent_decr()
        return "{\n" + ",\n".join(items) + "\n" + self.prefix + "}"


    def print_value(self, value):
        repr = None
        v = value.value
        c = value.comment
        if v is None:
            repr = "null"
        elif type(v) == str:
            repr = f'"{v}"'
        elif type(v) == float or type(v) == int:
            repr = str(v)
        elif type(v) == bool:
            repr = "true" if value else "false"
        elif type(v) == list:
            items = []
            self.indent_incr()
            for item in v:
                txt = self.prefix + self.print_value(item)
                items.append(txt)
            self.indent_decr()
            repr = "[\n" + ",\n".join(items) + "\n" + self.prefix + "]"
        elif type(v) == dict:
            items = []
            self.indent_incr()
            for key, item in v.items():
                txt = self.prefix + f'"{key}": ' + self.print_value(item)
                items.append(txt)
            self.indent_decr()
            repr = "{\n" + ",\n".join(items) + "\n" + self.prefix + "}"
        elif isinstance(v, Callable):
            repr = v.definition.accept(self)
        elif isinstance(v, UserType):
            repr = v.definition.accept(self)
        else:
            "print_value: Unknown value type!"
        return repr

    def print(self, value):
        repr = ""
        if isinstance(value, Expr):
            repr = value.accept(self)
        elif isinstance(value, Value):
            repr = self.print_value(value)
        return self.shorten_if_possible(repr)   
