
import sys
from typing import Any
from mindscript.ast import TokenType, Token, LexicalError, IncompleteExpression


Keywords = {
    "null": TokenType.NULL,
    "false": TokenType.BOOLEAN,
    "true": TokenType.BOOLEAN,
    "and": TokenType.AND,
    "or": TokenType.OR,
    "not": TokenType.NOT,
    "let": TokenType.LET,
    "do": TokenType.DO,
    "end": TokenType.END,
    "return": TokenType.RETURN,
    "break": TokenType.BREAK,
    "continue": TokenType.CONTINUE,
    "if": TokenType.IF,
    "then": TokenType.THEN,
    "elif": TokenType.ELIF,
    "else": TokenType.ELSE,
    "fun": TokenType.FUNCTION,
    "oracle": TokenType.ORACLE,
    "for": TokenType.FOR,
    "in": TokenType.IN,
    "from": TokenType.FROM,
    "type": TokenType.TYPECONS,
    "Type": TokenType.TYPE,
    "Null": TokenType.TYPE,
    "Str": TokenType.TYPE,
    "Int": TokenType.TYPE,
    "Num": TokenType.TYPE,
    "Bool": TokenType.TYPE,
    "Any": TokenType.TYPE,
    "Enum": TokenType.ENUM
}


class Lexer:

    def __init__(self):
        self.stream_id = "std"
        self.stream = {self.stream_id: ""}
        self.set_stream(self.stream_id)
        self.tokens = []

    def set_stream(self, stream_id: str):
        if stream_id not in self.stream:
            self.stream[stream_id] = ""
        self.stream_id = stream_id
        self.start = len(self.stream[stream_id])
        self.current = self.start
        self.whitespace = True

    def peek(self):
        c = self.stream[self.stream_id][self.current]
        return c

    def advance(self):
        c = self.stream[self.stream_id][self.current]
        # print(f"Scanning {c}")
        self.current += 1
        return c

    def rewind(self):
        self.current = self.start

    def forward(self):
        self.start = self.current

    def is_at_end(self):
        return self.current >= len(self.stream[self.stream_id])

    def add_token(self, ttype: TokenType, literal: Any = None):
        self.whitespace = False
        token = Token(
            ttype=ttype,
            literal=literal,
            index=self.start,
            buffer=self.stream_id
        )
        self.tokens.append(token)
        self.forward()
        return token

    def previous_token(self):
        if len(self.tokens) == 0:
            return None
        return self.tokens[-1]

    def skip_whitespace(self):
        self.whitespace = False
        while not self.is_at_end() and self.peek() in " \r\n":
            self.whitespace = True
            self.advance()
        self.forward()

    def is_digit(self, c: chr) -> bool:
        return "0" <= c and c <= "9"

    def is_nonzero_digit(self, c: chr) -> bool:
        return "1" <= c and c <= "9"

    def is_hex_digit(self, c: chr) -> bool:
        return ("0" <= c and c <= "9") or ("a" <= c and c <= "f") or ("A" <= c and c <= "F")    

    def is_id_start(self, c: chr) -> bool:
        return ("a" <= c and c <= "z") or ("A" <= c and c <= "Z") or (c == "_")

    def is_id(self, c: chr) -> bool:
        return ("a" <= c and c <= "z") or ("A" <= c and c <= "Z") or ("0" <= c and c <= "9") or (c == "_")

    def is_address(self, c: chr) -> bool:
        return self.is_id(c) or (c in ".-_~+#,%&=*;:@/")

    # See https://www.json.org/json-en.html
    def scan_string(self):
        lexeme = ""
        delimiter = self.advance()

        control = {
            "\"": "\"", 
            "\\": "\\", 
            "b": "\b",
            "f": "\f",
            "n": "\n",
            "r": "\r",
            "t": "\t",
        }

        while not self.is_at_end() and self.peek() != delimiter:
            c = self.advance()
            if c == "\\": # Control characters.
                if self.peek() in [delimiter, "\\", "/", "b", "f", "n", "r", "t"]:
                    cc = self.advance()
                    lexeme += control[cc]
                elif self.peek() == "u":
                    lexeme = c + self.advance()
                    for n in range(4):
                        if self.is_at_end() or not self.is_hex_digit(self.peek()):
                            self.error("Unicode was not terminated.")
                            self.advance()
                            return None
                        lexeme += self.advance()
                    lexeme = lexeme.encode().decode("unicode_escape")
                else:
                    return None
            else:
                lexeme += c
        if self.is_at_end():
            self.error("String was not terminated.")
        self.advance()
        return lexeme

    def scan_integer(self):
        lexeme = ""
        if not self.is_at_end() and self.is_nonzero_digit(self.peek()):
            lexeme += self.advance()
        while not self.is_at_end() and self.is_digit(self.peek()):
            lexeme += self.advance()
        # Exclude possibility of a float.
        if not self.is_at_end() and self.peek() in [".", "e", "E"]:
            return None
        return lexeme

    # See https://www.json.org/json-en.html
    def scan_float(self):
        lexeme = ""
        if not self.is_at_end() and self.peek() == "0":
            lexeme += self.advance()
        elif not self.is_at_end() and self.is_nonzero_digit(self.peek()):
            lexeme += self.advance()
            while not self.is_at_end() and self.is_digit(self.peek()):
                lexeme += self.advance()
        else:
            return None
        # Fraction
        if not self.is_at_end() and self.peek() == ".":
            lexeme += self.advance()
            while not self.is_at_end() and self.is_digit(self.peek()):
                lexeme += self.advance()
        # Exponent
        if not self.is_at_end() and self.peek() in ["e", "E"]:
            lexeme += self.advance()
            if not self.is_at_end() and self.peek() in ["-", "+"]:
                lexeme += self.advance()
            if not self.is_at_end() and self.is_digit(self.peek()):
                lexeme += self.advance()
            else:
                return None 
            while not self.is_at_end() and self.is_digit(self.peek()):
                lexeme += self.advance()
        return lexeme

    def ignore_until_newline(self):
        while not self.is_at_end():
            c = self.advance()
            if c == "\n":
                return

    def scan_annotation(self):
        lexeme = ""
        line = ""
        while not self.is_at_end():
            c = self.advance()
            line += c
            if c == "\n":
                lexeme += line.strip() + "\n"
                line = ""
                while not self.is_at_end() and self.peek() in "\r\t ":
                    self.advance()
                if self.is_at_end():
                    return IncompleteExpression()
                if self.peek() == "#":
                    self.advance()
                elif self.peek() == "\n":
                    # Quit annotation.
                    return None
                else:
                    return lexeme.strip()
        raise IncompleteExpression()

    def scan_id(self):
        lexeme = self.advance()
        while not self.is_at_end() and self.is_id(self.peek()):
            lexeme += self.advance()
        return lexeme

    def linecol(self, buffer: str, index: int):
        padded = self.stream[buffer] + "\n"
        lines = padded.splitlines(True)

        # Determine line, col.
        line, col, idx = 0, 0, index
        for l in lines:
            if idx >= len(l):
                idx -= len(l)
                line += 1
            else:
                col = idx
                break
        return line, col

    def report_error(self, buffer: str, index: int, errtype: str, msg: str):
        line, col = self.linecol(buffer, index)
        padded = self.stream[buffer] + "\n"
        lines = padded.splitlines(True)

        error_msg = f"{errtype}: In {buffer}, line {line+1}, near\n"
        if line > 0:
            error_msg += lines[line-1]
        error_msg += lines[line]
        error_msg += " " * col + "^\n"
        error_msg += msg
        print(error_msg, file=sys.stderr, flush=True)

    def error(self, msg: str):
        self.report_error(self.stream_id, self.start, "LEXICAL ERROR", msg)
        raise LexicalError(msg)

    def scan_token(self):
        self.skip_whitespace()
        if self.is_at_end():
            return self.add_token(TokenType.EOF)

        c = self.advance()

        # Single character.
        if c == "(":
            if self.whitespace:
                return self.add_token(TokenType.LROUND, "(")
            return self.add_token(TokenType.CLROUND, "(")

        if c == ")":
            return self.add_token(TokenType.RROUND, ")")

        if c == "[":
            if self.whitespace:
                return self.add_token(TokenType.LSQUARE, "[")
            return self.add_token(TokenType.CLSQUARE, "[")

        if c == "]":
            return self.add_token(TokenType.RSQUARE, "]")

        if c == "{":
            return self.add_token(TokenType.LCURLY, "{")

        if c == "}":
            return self.add_token(TokenType.RCURLY, "}")

        if c == "+":
            return self.add_token(TokenType.PLUS, "+")

        if c == "*":
            return self.add_token(TokenType.MULT, "*")

        if c == "/":
            return self.add_token(TokenType.DIV, "/")

        if c == "%":
            return self.add_token(TokenType.MOD, "%")

        if c == ":":
            return self.add_token(TokenType.COLON, ":")

        if c == ",":
            return self.add_token(TokenType.COMMA, ",")

        if c == "?":
            return self.add_token(TokenType.QUESTION, "?")

        if c == "." and not self.is_digit(self.peek()):
            return self.add_token(TokenType.PERIOD, ".")


        # Double characters.

        if c == "-":
            if not self.is_at_end() and self.peek() == ">":
                self.advance()
                return self.add_token(TokenType.ARROW, "->")
            return self.add_token(TokenType.MINUS, "-")

        if c == "=":
            if not self.is_at_end() and self.peek() == "=":
                self.advance()
                return self.add_token(TokenType.EQ, "==")
            return self.add_token(TokenType.ASSIGN, "=")

        if c == "!":
            if not self.is_at_end() and self.peek() == "=":
                self.advance()
                return self.add_token(TokenType.NEQ, "!=")
            return self.add_token(TokenType.BANG, "!")

        if c == "<":
            if not self.is_at_end() and self.peek() == "=":
                self.advance()
                return self.add_token(TokenType.LESS_EQ, "<=")
            return self.add_token(TokenType.LESS, "<")

        if c == ">":
            if not self.is_at_end() and self.peek() == "=":
                self.advance()
                return self.add_token(TokenType.GREATER_EQ, ">=")
            return self.add_token(TokenType.GREATER, ">")

        # Multi-characters.

        if c == "#":
            if not self.is_at_end() and self.peek() == "#":
                self.ignore_until_newline()
                self.add_token(TokenType.HASH, "")
                return self.tokens.pop()
            lexeme = self.scan_annotation()
            if lexeme is None:
                return self.add_token(TokenType.NULL, None)
            return self.add_token(TokenType.HASH, lexeme)

        if c == '"' or c == "'":
            self.rewind()
            lexeme = self.scan_string()
            prev = self.previous_token()
            if lexeme is None:
                self.rewind()
            elif prev and prev.ttype == TokenType.PERIOD:
                return self.add_token(TokenType.ID, lexeme)
            return self.add_token(TokenType.STRING, str(lexeme))

        if self.is_digit(c):
            # Integer?
            self.rewind()
            lexeme = self.scan_integer()
            if lexeme:
                return self.add_token(TokenType.INTEGER, int(lexeme))
            # Float?
            self.rewind()
            lexeme = self.scan_float()
            if lexeme:
                return self.add_token(TokenType.NUMBER, float(lexeme))
            self.rewind()

        if self.is_id_start(c):
            self.rewind()
            lexeme = self.scan_id()
            prev = self.previous_token()
            if lexeme is None:
                self.rewind()
            elif prev and prev.ttype == TokenType.PERIOD:
                return self.add_token(TokenType.ID, lexeme)
            elif lexeme in Keywords:
                ttype = Keywords[lexeme]
                if ttype == TokenType.NULL:
                    return self.add_token(ttype, None)
                elif ttype == TokenType.BOOLEAN and lexeme == "false":
                    return self.add_token(ttype, False)
                elif ttype == TokenType.BOOLEAN and lexeme == "true":
                    return self.add_token(ttype, True)
                return self.add_token(ttype, lexeme)
            return self.add_token(TokenType.ID, lexeme)

        self.error("Unexpected character.")

        return self.add_token(TokenType.EOF)  # Change this for error handling!

    def scan(self, code: str, buffer: str):
        self.set_stream(buffer)
        self.tokens = []
        self.stream[self.stream_id] += code.replace("\t", "    ")
        while self.scan_token().ttype != TokenType.EOF:
            pass
        return self.tokens
