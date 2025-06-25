import copy
from typing import List
import mindscript.ast as ast
from mindscript.ast import TokenType, Token
from mindscript.lexer import Lexer

###
# BNF of grammar:
# ```
#     program     ::= chunk EOF
#     chunk       ::= expression*
#     expression  ::= ANNOTATION? "return" "~(" expression ")"
#                     | ANNOTATION? "break" "~(" expression ")"
#                     | ANNOTATION? "continue" "~(" expression ")"
#                     | ANNOTATION? assignment
#     assignment  ::= disjunction "=" expression | disjunction
#     disjunction ::= conjunction ("or" conjunction)*
#     conjunction ::= equality ("and" equality)*
#     equality    ::= comparison (("=="|"!=") comparison)*
#     comparison  ::= term (("<"|"<="|">"|">=") term)*
#     term        ::= factor (("+"|"-") factor)*
#     factor      ::= unary (("*"|"/"|"%") unary)*
#     unary       ::= ("not"|"-") call | call
#     call        ::= primary ( "~(" expression* ")" | "." ID | "~[" expression "]" )*
#
#     primary     ::= INTEGER | NUMBER | STRING | BOOLEAN | NULL | array | map |
#                     type | function | oracle | target | ( "~(" | "(" ) expression ")" |
#                     block | conditional | for
#     array       ::= "[" (expression ("," expression)*)? "]"
#     map         ::= "{" (item ("," item)*)? "}"
#     item        ::= ANNOTATION? key ":" expression
#     key         ::= STRING | IDENTIFIER
#
#     block       ::= "do" chunk "end"
#     conditional ::= "if" expression "then" chunk
#                     ("elif" expression "then" chunk)*
#                     ("else" chunk)? "end"
#     while       ::= "while" expression control
#     for         ::= "for" expression "in" expression block
#     target      ::= ID | declaration
#     declaration ::= "let" ID
#     function    ::= "fun" "~(" parameter* ")"
#                       ("->" type_expr)? block
#     oracle      ::= "oracle" "~(" parameter* ")"
#                       ("->" type_expr)? ("from" array)?
#     parameter   ::= ANNOTATION? ID (":" type_expr)?
#
#     type        ::= "type" type_expr
#     type_expr   ::= ANNOTATION? type_expr
#     type_binary ::= type_unary "->" type_expr | type_unary
#     type_unary  ::= type_prim "?" | type_prim
#     type_prim   ::= ID | TYPE | type_enum | type_arr | type_map | "(" type_expr ")"
#     type_enum   ::= "Enum" array
#     type_arr    ::= "[" type_expr "]"
#     type_map    ::= "{" (type_item ("," type_item)*)? "}"
#     type_item   ::= ANNOTATION? key "!"? ":" type_expr
# ```
###


class Parser:
    def __init__(self, interactive=False):
        self.lexer = Lexer()
        self.interactive = interactive
        self.reset()

    def reset(self):
        self.ast = None
        self.current = 0
        self.start = 0
        self.tokens = []

    def is_at_end(self) -> bool:
        return self.tokens[self.current].ttype == TokenType.EOF

    def peek(self) -> Token:
        return self.tokens[self.current]

    def advance(self) -> Token:
        token = self.tokens[self.current]
        # print(f"Token: {token}")
        self.current += 1
        self.start = self.current
        return token

    def check(self, ttype: TokenType) -> bool:
        return (self.tokens[self.current].ttype == ttype)

    def previous(self) -> Token:
        return self.tokens[self.current - 1]

    def match(self, ttypes: List[TokenType]) -> bool:
        for ttype in ttypes:
            if self.check(ttype):
                self.advance()
                return True
        return False

    def error(self, token: Token, msg: str) -> None:
        self.lexer.report_error(token.buffer, token.index, "SYNTAX ERROR", msg)
        raise ast.SyntaxError(msg)

    def consume(self, ttype: TokenType, fail_msg: str) -> bool:
        if self.interactive and self.is_at_end():
            raise ast.IncompleteExpression()
        if self.is_at_end() or not self.check(ttype):
            self.error(self.peek(), fail_msg)
        return self.advance()

    def synchronize(self):
        token = self.peek()
        line_before, _ = self.lexer.linecol(token.buffer, token.index)
        while not self.is_at_end():
            self.advance()
            token = self.peek()
            line_current, _ = self.lexer.linecol(token.buffer, token.index)
            if not self.is_at_end() and line_before < line_current:
                return

    def any_type_terminal(self, buffer: str, index: int):
        return ast.TypeTerminal(
            token=Token(
                ttype=TokenType.TYPE,
                literal="Any",
                buffer=buffer,
                index=index
            )
        )

    def null_type_terminal(self, buffer: str, index: int):
        return ast.TypeTerminal(
            token=Token(
                ttype=TokenType.TYPE,
                literal="Null",
                buffer=buffer,
                index=index
            )
        )

    def null_terminal(self, buffer: str, index: int):
        return ast.Terminal(
            token=Token(
                ttype=TokenType.NULL,
                literal=None,
                buffer=buffer,
                index=index
            )
        )

    def parse_program(self):
        program = []
        contains_error = False
        while not self.is_at_end():
            try:
                expression = self.parse_expression()
                program.append(expression)
            except ast.SyntaxError as e:
                self.synchronize()
                contains_error = e
        self.advance()
        if contains_error:
            raise ast.SyntaxError("The code contains errors.")
        return ast.Program(program=program)

    def parse_expression(self):
        if self.match([TokenType.RETURN, TokenType.BREAK, TokenType.CONTINUE]):
            operator = self.previous()
            self.consume(TokenType.CLROUND,
                         f"Expected '(' after '{operator.literal}'.")
            expr = self.parse_expression()
            self.consume(TokenType.RROUND,
                         f"Expected closing ')' after expression.")
            return ast.Unary(operator=operator, expr=expr)
        return self.parse_expression()

    def parse_expression(self):
        annotation = None
        if self.match([TokenType.HASH]):
            operator = self.previous()
            annotation = Token(
                ttype=TokenType.STRING, 
                buffer=operator.buffer, 
                index=operator.index, 
                literal=operator.literal
            )

        if self.match([TokenType.RETURN, TokenType.BREAK, TokenType.CONTINUE]):
            operator = self.previous()
            self.consume(TokenType.CLROUND,
                         f"Expected '(' after '{operator.literal}'.")
            expr = self.parse_expression()
            self.consume(TokenType.RROUND,
                         f"Expected closing ')' after expression.")
            expr = ast.Unary(operator=operator, expr=expr)
        else:
            expr = self.parse_assignment()

        if annotation:
            return ast.Annotation(operator=operator, annotation=annotation, expr=expr)
        return expr

    def parse_assignment(self):
        mapping = self.parse_disjunction()
        if self.match([TokenType.ASSIGN]):
            operator = self.previous()
            expr = self.parse_expression()
            if isinstance(mapping, ast.Terminal) and mapping.token.ttype == TokenType.ID:
                return ast.Assign(target=mapping, operator=operator, expr=expr)
            elif isinstance(mapping, ast.Declaration):
                return ast.Assign(target=mapping, operator=operator, expr=expr)
            elif isinstance(mapping, ast.ArrayGet):
                setter = ast.ArraySet(operator=mapping.operator,
                                      expr=mapping.expr,
                                      index=mapping.index)
                return ast.Assign(target=setter, operator=operator, expr=expr)
            elif isinstance(mapping, ast.ObjectGet):
                setter = ast.ObjectSet(operator=mapping.operator,
                                       expr=mapping.expr,
                                       index=mapping.index)
                return ast.Assign(target=setter, operator=operator, expr=expr)
            elif isinstance(mapping, ast.Array):
                return ast.Assign(target=mapping, operator=operator, expr=expr)
            elif isinstance(mapping, ast.Map):
                return ast.Assign(target=mapping, operator=operator, expr=expr)
            self.error(operator, "Invalid assignment target.")
        return mapping

    def parse_disjunction(self):
        conjunction = self.parse_conjunction()
        while self.match([TokenType.OR]):
            op = self.previous()
            right = self.parse_conjunction()
            conjunction = ast.Binary(
                left=conjunction, operator=op, right=right)
        return conjunction

    def parse_conjunction(self):
        equality = self.parse_equality()
        while self.match([TokenType.AND]):
            op = self.previous()
            right = self.parse_equality()
            equality = ast.Binary(left=equality, operator=op, right=right)
        return equality

    def parse_equality(self):
        equality = self.parse_comparison()
        while self.match([TokenType.EQ, TokenType.NEQ]):
            op = self.previous()
            right = self.parse_comparison()
            equality = ast.Binary(left=equality, operator=op, right=right)
        return equality

    def parse_comparison(self):
        comparison = self.parse_term()
        while self.match([TokenType.LESS, TokenType.LESS_EQ, TokenType.GREATER, TokenType.GREATER_EQ]):
            op = self.previous()
            right = self.parse_term()
            comparison = ast.Binary(left=comparison, operator=op, right=right)
        return comparison

    def parse_term(self):
        term = self.parse_factor()
        while self.match([TokenType.PLUS, TokenType.MINUS]):
            op = self.previous()
            right = self.parse_factor()
            term = ast.Binary(left=term, operator=op, right=right)
        return term

    def parse_factor(self):
        factor = self.parse_unary()
        while self.match([TokenType.MULT, TokenType.DIV, TokenType.MOD]):
            op = self.previous()
            right = self.parse_unary()
            factor = ast.Binary(left=factor, operator=op, right=right)
        return factor

    def parse_unary(self):
        if self.match([TokenType.MINUS, TokenType.NOT]):
            op = self.previous()
            call = self.parse_call()
            return ast.Unary(operator=op, expr=call)
        return self.parse_call()

    def parse_call(self):
        primary = self.parse_primary()
        while self.match([TokenType.CLROUND, TokenType.PERIOD, TokenType.CLSQUARE]):
            operator = self.previous()
            if operator.ttype == TokenType.CLROUND:
                arguments = []
                if not self.check(TokenType.RROUND):
                    argument = self.parse_expression()
                    arguments.append(argument)
                    while self.match([TokenType.COMMA]):
                        argument = self.parse_expression()
                        arguments.append(argument)
                self.consume(TokenType.RROUND,
                             "Expected closing ')'.")
                if len(arguments) == 0:
                    arguments.append(self.null_terminal(
                        operator.buffer, operator.index))
                primary = ast.Call(expr=primary, operator=operator,
                                   arguments=arguments)
            elif operator.ttype == TokenType.CLSQUARE:
                index = self.parse_expression()
                primary = ast.ArrayGet(
                    operator=operator, expr=primary, index=index)
                self.consume(TokenType.RSQUARE, "Expected closing ']'.")
            elif operator.ttype == TokenType.PERIOD:
                if self.match([TokenType.ID, TokenType.STRING]):
                    # Syntax sugar: a.field => a."field"
                    token = self.previous()
                    token.ttype = TokenType.STRING
                    index = ast.Terminal(token=token)
                    primary = ast.ObjectGet(
                        operator=operator, expr=primary, index=index)
                else:
                    self.error(operator, "Expected a property name.")
        return primary

    def parse_primary(self):
        # print(f"parse_primary: next token = {self.peek()}")
        if self.match([TokenType.ID, TokenType.INTEGER, TokenType.NUMBER, TokenType.STRING, TokenType.BOOLEAN, TokenType.NULL]):
            token = self.previous()
            return ast.Terminal(token=token)
        if self.match([TokenType.TYPE, TokenType.ENUM]):
            self.error(self.previous(),
                       "Type atom without type constructor.")
        if self.check(TokenType.LSQUARE) or self.check(TokenType.CLSQUARE):
            return self.parse_array()
        if self.check(TokenType.LCURLY):
            return self.parse_map()
        if self.check(TokenType.TYPECONS):
            return self.parse_type_def()
        if self.check(TokenType.DO):
            return self.parse_block()
        if self.check(TokenType.IF):
            return self.parse_conditional()
        if self.check(TokenType.FOR):
            return self.parse_for()
        if self.check(TokenType.FUNCTION) or self.check(TokenType.ORACLE):
            return self.parse_function()
        if self.match([TokenType.LROUND, TokenType.CLROUND]):
            expr = self.parse_expression()
            self.consume(TokenType.RROUND, "Expected ')' after expression.")
            return ast.Grouping(expr=expr)
        if self.check(TokenType.ID) or self.check(TokenType.LET):
            return self.parse_target()
        if self.peek().ttype in [TokenType.RETURN, TokenType.BREAK, TokenType.CONTINUE]:
            self.error(
                self.peek(), f"Invalid '{self.peek().literal}' expression.")
        # Only in interactive mode: Expected a missing expression.
        if self.check(TokenType.EOF) and self.interactive:
            raise ast.IncompleteExpression()
        self.error(self.peek(), "Expected an expression.")

    def parse_array(self):
        array = []
        if self.match([TokenType.LSQUARE, TokenType.CLSQUARE]):
            if self.match([TokenType.RSQUARE]):
                return ast.Array(array=[])
            expr = self.parse_expression()
            array.append(expr)
            while self.match([TokenType.COMMA]):
                expr = self.parse_expression()
                array.append(expr)
            self.consume(TokenType.RSQUARE,
                         "Expected closing ']' after list of expressions.")
            return ast.Array(array=array)
        self.error(self.peek(), "Expected an array expression.")

    def parse_map(self):
        dictionary = {}
        self.consume(TokenType.LCURLY, "Expected opening '{'.")
        if self.match([TokenType.RCURLY]):
            return ast.Map(map={})
        [key, expr] = self.parse_item()
        dictionary[key.literal] = expr
        while self.match([TokenType.COMMA]):
            [key, expr] = self.parse_item()
            dictionary[key.literal] = expr
        self.consume(TokenType.RCURLY,
                     "Expected closing '}' after list of members.")
        return ast.Map(map=dictionary)

    def parse_item(self):
        if self.match([TokenType.HASH]):
            operator = self.previous()
            annotation = Token(
                ttype=TokenType.STRING, 
                buffer=operator.buffer, 
                index=operator.index, 
                literal=operator.literal
            )
            key = self.parse_key()
            self.consume(TokenType.COLON, "Expected ':' after member key.")
            expr = self.parse_expression()
            return [key, ast.Annotation(operator=operator, annotation=annotation, expr=expr)]
        key = self.parse_key()
        self.consume(TokenType.COLON, "Expected ':' after member key.")
        expr = self.parse_expression()
        return [key, expr]

    def parse_key(self):
        if self.match([TokenType.ID]):
            key = self.previous()
            new_key = Token(
                ttype=TokenType.STRING,
                buffer=key.buffer,
                index=key.index,
                literal=key.literal)
            return new_key
        elif self.match([TokenType.STRING]):
            key = self.previous()
            return key
        # Only in interactive mode: Expected a missing expression.
        if self.check(TokenType.EOF) and self.interactive:
            raise ast.IncompleteExpression()
        self.error(self.peek(), "Expected a member key.")

    def parse_chunk_until(self, ends: List[Token]):
        exprs = []
        while self.peek().ttype not in ends:
            expr = self.parse_expression()
            exprs.append(expr)
        return ast.Block(exprs=exprs)

    def parse_block(self):
        self.consume(TokenType.DO, "Expected 'do' keyword.")
        block = self.parse_chunk_until([TokenType.END])
        self.consume(TokenType.END, "Expected 'end' keyword.")
        return block

    def parse_conditional(self):
        operators = []
        conds = []
        exprs = []
        default = None
        if self.match([TokenType.IF]):
            operators.append(self.previous())
            cond = self.parse_expression()
            conds.append(cond)
            self.consume(TokenType.THEN, "Expected 'then' after condition.")
            chunk = self.parse_chunk_until(
                [TokenType.END, TokenType.ELIF, TokenType.ELSE])
            exprs.append(chunk)
            while self.match([TokenType.ELIF]):
                operators.append(self.previous())
                cond = self.parse_expression()
                conds.append(cond)
                self.consume(TokenType.THEN,
                             "Expected 'then' after condition.")
                chunk = self.parse_chunk_until(
                    [TokenType.END, TokenType.ELIF, TokenType.ELSE])
                exprs.append(chunk)
            if self.match([TokenType.ELSE]):
                default = self.parse_chunk_until([TokenType.END])
            self.consume(
                TokenType.END, "Expected closing 'end' after conditional expression.")
            return ast.Conditional(operators=operators, conds=conds, exprs=exprs, default=default)

    def parse_for(self):
        if self.match([TokenType.FOR]):
            operator = self.previous()
            target = self.parse_expression()
            self.consume(TokenType.IN, "Expected 'in' keyword.")
            iterator = self.parse_expression()
            expr = self.parse_block()
            return ast.For(operator=operator, target=target, iterator=iterator, expr=expr)

    def parse_function(self):
        if self.match([TokenType.FUNCTION, TokenType.ORACLE]):
            operator = self.previous()
            self.consume(TokenType.CLROUND,
                         f"Expected '(' after '{operator.literal}' keyword.")
            params = []
            ptypes = []
            if not self.check(TokenType.RROUND):
                param, ptype = self.parse_parameter()
                params.append(param)
                ptypes.append(ptype)
                while self.match([TokenType.COMMA]):
                    param, ptype = self.parse_parameter()
                    params.append(param)
                    ptypes.append(ptype)
            self.consume(
                TokenType.RROUND, "Expected closing ')' after function parameters.")
            if len(params) == 0:
                params.append(Token(
                    ttype=TokenType.ID,
                    literal="_",
                    buffer=operator.buffer,
                    index=operator.index))
                ptypes.append(self.null_type_terminal(
                    operator.buffer, operator.index))

            if self.match([TokenType.ARROW]):
                types = self.parse_type_expr()
            else:
                types = self.any_type_terminal(operator.buffer, operator.index)

            for ptype in reversed(ptypes):
                types = ast.TypeBinary(
                    operator=operator, left=ptype, right=types)

            expr = None
            if operator.ttype == TokenType.FUNCTION:
                expr = self.parse_block()
            elif self.match([TokenType.FROM]):
                expr = self.parse_expression()
            else:
                expr = ast.Array(array=[])
            return ast.Function(operator=operator, parameters=params, types=types, expr=expr)

    def parse_parameter(self):
        annotation = None
        if self.match([TokenType.HASH]):
            operator = self.previous()
            annotation = Token(
                ttype=TokenType.STRING, 
                buffer=operator.buffer, 
                index=operator.index,
                literal=operator.literal
            )

        self.consume(TokenType.ID, "Expected a parameter name.")
        param = self.previous()

        if self.match([TokenType.COLON]):
            ptype = self.parse_type_expr()
            if type(ptype) == ast.TypeBinary:
                ptype = ast.TypeGrouping(expr=ptype)
        else:
            last_token = self.previous()
            ptype = self.any_type_terminal(last_token.buffer, last_token.index)

        if annotation is not None:
            ptype = ast.TypeAnnotation(
                operator=operator, annotation=annotation, expr=ptype)

        return [param, ptype]

    def parse_target(self):
        if self.match([TokenType.ID]):
            token = self.previous()
            return ast.Terminal(token=token)
        return self.parse_declaration()

    def parse_declaration(self):
        if self.match([TokenType.LET]):
            operator = self.previous()
            token = self.consume(TokenType.ID, "Expected an identifier.")
            return ast.Declaration(operator=operator, token=token)
        self.error(self.peek(), "Invalid expression.")

    def parse_type_def(self):
        if self.match([TokenType.TYPECONS]):
            operator = self.previous()
            expr = self.parse_type_expr()
            node = ast.TypeDefinition(operator=operator, expr=expr)
            return node

    def parse_type_expr(self):
        if self.match([TokenType.HASH]):
            operator = self.previous()
            annotation = Token(
                ttype=TokenType.STRING, 
                buffer=operator.buffer, 
                index=operator.index, 
                literal=operator.literal
            )
            expr = self.parse_type_expr()
            return ast.TypeAnnotation(operator=operator, annotation=annotation, expr=expr)
        expr = self.parse_type_binary()
        return expr

    def parse_type_binary(self):
        left = self.parse_type_unary()
        if self.match([TokenType.ARROW]):
            operator = self.previous()
            expr = self.parse_type_expr()
            while isinstance(expr, ast.TypeGrouping):
                expr = expr.expr
            return ast.TypeBinary(left=left, operator=operator, right=expr)
        return left

    def parse_type_unary(self):
        expr = self.parse_type_prim()
        if self.match([TokenType.QUESTION]):
            operator = self.previous()
            return ast.TypeUnary(operator=operator, expr=expr)
        return expr

    def parse_type_prim(self):
        if self.match([TokenType.ID, TokenType.TYPE]):
            token = self.previous()
            return ast.TypeTerminal(token=token)
        if self.check(TokenType.ENUM):
            return self.parse_type_enum()
        if self.check(TokenType.LSQUARE) or self.check(TokenType.CLSQUARE):
            return self.parse_type_arr()
        if self.check(TokenType.LCURLY):
            return self.parse_type_map()
        if self.match([TokenType.LROUND, TokenType.CLROUND]):
            expr = self.parse_type_expr()
            self.consume(TokenType.RROUND,
                         "Expected ')' after type expression.")
            return ast.TypeGrouping(expr=expr)
        # Only in interactive mode: Expected a missing expression.
        if self.check(TokenType.EOF) and self.interactive:
            raise ast.IncompleteExpression()
        self.error(self.peek(), "Expected a type expression.")

    def parse_type_enum(self):
        if self.match([TokenType.ENUM]):
            operator = self.previous()
            if self.check(TokenType.EOF) and self.interactive:
                raise ast.IncompleteExpression()
            if self.check(TokenType.LSQUARE) or self.check(TokenType.CLSQUARE):
                expr = self.parse_array()
            else:
                self.error(self.peek(), "Expected an array after Enum.")
            return ast.TypeEnum(operator=operator, expr=expr)
        self.error(self.peek(), "Expected an Enum expression.")

    def parse_type_arr(self):
        if self.match([TokenType.LSQUARE, TokenType.CLSQUARE]):
            expr = self.parse_type_expr()
            self.consume(TokenType.RSQUARE,
                         "Expected closing ']' after type expression.")
            return ast.TypeArray(expr=expr)

    def parse_type_map(self):
        dictionary = {}
        required = {}
        self.consume(TokenType.LCURLY, "Expected opening '{'.")
        if self.match([TokenType.RCURLY]):
            return ast.TypeMap(map={}, required={})
        [key, req, expr] = self.parse_type_item()
        dictionary[key.literal] = expr
        if req:
            required[key.literal] = True
        while self.match([TokenType.COMMA]):
            [key, req, expr] = self.parse_type_item()
            dictionary[key.literal] = expr
            if req:
                required[key.literal] = True
        self.consume(TokenType.RCURLY,
                     "Expected closing '}' after list of members.")
        return ast.TypeMap(map=dictionary, required=required)

    def parse_type_item(self):
        required = False
        if self.match([TokenType.HASH]):
            operator = self.previous()
            annotation = Token(
                ttype=TokenType.STRING, 
                buffer=operator.buffer, 
                index=operator.index, 
                literal=operator.literal
            )
            key = self.parse_key()
            required = True if self.match([TokenType.BANG]) else False
            self.consume(TokenType.COLON, "Expected ':' after member key.")
            expr = self.parse_type_expr()
            return [key, required, ast.TypeAnnotation(operator=operator, annotation=annotation, expr=expr)]
        key = self.parse_key()
        required = True if self.match([TokenType.BANG]) else False
        self.consume(TokenType.COLON, "Expected ':' after member key.")
        expr = self.parse_type_expr()
        return [key, required, expr]

    def parse(self, code: str, buffer: str):
        self.reset()

        # Scan and parse.
        tree = None
        previous_lexer = copy.deepcopy(self.lexer)

        try:
            tokens = self.lexer.scan(code, buffer)
            if tokens is None:
                return None
            self.tokens = tokens
            tree = self.parse_program()
            if tree is None:
                return None
        except (ast.LexicalError, ast.SyntaxError) as e:
            # print("Lexical or Syntax Error has occurred.")
            self.lexer = previous_lexer
        except ast.IncompleteExpression as e:
            # print("Detected incomplete expression.")
            self.lexer = previous_lexer
            raise (e)

        # print(f"parser.parse: tree = {tree}")

        return tree
