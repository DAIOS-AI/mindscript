import re
from typing import List, Dict
from mindscript.ast import TokenType, Expr, TypeArray
from mindscript.objects import MObject, MValue, MType, MFunction

TABLEN = 4
MAXDEPTH = 4
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
        string = re.sub(r" +", " ", string)
        string = re.sub(r" (\]|\)|\})", r"\1", string)
        string = re.sub(r"(\[|\(|\{) ", r"\1", string)
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
        return node.expr.accept(self)

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
        return f"{op}({expr})"  # Should be "return", "break", "continue"

    def grouping(self, node):
        if self.is_max_depth():
            return "(...)"
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
            literal = repr(literal)
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
        if self.is_max_depth():
            return "[...]"
        return "[\n" + ",\n".join(items) + "\n" + self.prefix + "]"

    def map(self, node):
        self.indent_incr()
        items = []
        for key, expr in node.map.items():
            txt = self.prefix + key + ": " + expr.accept(self)
            items.append(txt)
        self.indent_decr()
        if self.is_max_depth():
            return "{...}"
        return "{\n" + ",\n".join(items) + "\n" + self.prefix + "}"

    def print_chunk(self, node):
        if self.is_max_depth():
            return "..."
        self.indent_incr()
        content = ""
        for expr in node.exprs:
            content += self.prefix + expr.accept(self) + "\n"
        self.indent_decr()
        return f"{content}"

    def block(self, node):
        if self.is_max_depth():
            return "do ... end"
        content = "do\n"
        content += self.print_chunk(node)
        content += self.prefix + "end"
        return content

    def conditional(self, node):
        if self.is_max_depth():
            return "if ... end"
        cond = node.conds[0].accept(self)
        expr = node.exprs[0]
        content = "if " + cond + " then\n" + self.print_chunk(expr)
        for n in range(1, len(node.conds)):
            cond = node.conds[n].accept(self)
            expr = node.exprs[n]
            content += self.prefix + "elif " + cond + \
                " then\n" + self.print_chunk(expr)
        if node.default is not None:
            expr = node.default
            content += self.prefix + "else\n" + self.print_chunk(expr)
        content += self.prefix + "end"
        return content

    def forloop(self, node):
        if self.is_max_depth():
            return "for ... end"
        target = node.target.accept(self)
        iterator = node.iterator.accept(self)
        block = node.expr.accept(self)
        content = "for " + target + " in " + iterator + " " + block
        return content

    def call(self, node):
        callee = node.expr.accept(self)
        arg_list = [arg.accept(self) for arg in node.arguments]
        arguments = "(" + ", ".join(arg_list) + ")"
        return callee + arguments

    def function(self, node):
        parameters = []
        types = node.types
        for param in node.parameters:
            # print(f"printer.function: types = {types}")
            param_name = param.literal
            param_type = types.left.accept(self)
            parameters.append(f"{param_name}: {param_type}")
            types = types.right
        out_type = types.accept(self)
        expr = node.expr.accept(self)
        param_list = ", ".join(parameters)
        return f"fun({param_list}) -> {out_type} {expr}"

    def type_definition(self, node):
        expr = node.expr.accept(self)
        content = f"type {expr}"
        return content

    def type_annotation(self, node):
        annotation = node.annotation.literal
        return node.expr.accept(self)

    def type_terminal(self, node):
        return node.token.literal

    def type_grouping(self, node):
        if self.is_max_depth():
            return "(...)"
        expr = node.expr.accept(self)
        return f"({expr})"

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

    def type_enum(self, node):
        if self.is_max_depth():
            return "Enum(...)"
        valuestxt = self.print_value(node.values)
        return f"Enum {valuestxt}"

    def type_array(self, node):
        if self.is_max_depth():
            return "[...]"
        expr = node.expr.accept(self)
        return f"[{expr}]"

    def type_map(self, node):
        if self.is_max_depth():
            return "{...}"
        self.indent_incr()
        items = []
        for key, expr in node.map.items():
            if key in node.required:
                key = key + "!"
            txt = self.prefix + key + ": " + expr.accept(self)
            items.append(txt)
        self.indent_decr()
        return "{\n" + ",\n".join(items) + "\n" + self.prefix + "}"

    def print_value(self, value):
        txt = None
        if isinstance(value, MValue):
            v = value.value
            c = value.annotation
            if v is None:
                txt = "null"
            elif type(v) == str:
                txt = repr(f'{v}')
                txt = '"' + txt[1:-1] + '"'
            elif type(v) == float or type(v) == int:
                txt = str(v)
            elif type(v) == bool:
                txt = "true" if v else "false"
            elif type(v) == list:
                if self.is_max_depth():
                    return "[...]"
                items = []
                self.indent_incr()
                for item in v:
                    txt = self.prefix + self.print_value(item)
                    items.append(txt)
                self.indent_decr()
                txt = "[\n" + ",\n".join(items) + "\n" + self.prefix + "]"
            elif type(v) == dict:
                if self.is_max_depth():
                    return "{...}"
                items = []
                self.indent_incr()
                for key, item in v.items():
                    txt = self.prefix + f'"{key}": ' + self.print_value(item)
                    items.append(txt)
                self.indent_decr()
                txt = "{\n" + ",\n".join(items) + "\n" + self.prefix + "}"
            else:
                raise ValueError(
                    "print_value received an MValue that is not recognized.")
        elif isinstance(value, MFunction):
            items = []
            for param, ptype in zip(value.params, value.intypes):
                txt = param.literal + ":" +  ptype.definition.accept(self)
                items.append(txt)
            self.indent_incr()
            prefix = "\n" + self.prefix + " -> "
            self.indent_decr()
            txt = prefix.join(items)
            txt += prefix + value.outtype.definition.accept(self)
        elif isinstance(value, MType):
            txt = "type " + value.definition.accept(self)
        else:
            "print_value: Unknown value type!"
        return self.shorten_if_possible(txt)

    def print(self, value):
        txt = ""
        if isinstance(value, Expr):
            txt = value.accept(self)
        elif isinstance(value, MObject):
            txt = self.print_value(value)
        return self.shorten_if_possible(txt)
