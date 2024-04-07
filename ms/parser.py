import copy
from typing import List
import ms.ast as ast
from ms.ast import TokenType, Token
from ms.lexer import Lexer

###
# BNF of grammar:
# ```
#     program     -> chunk EOF
#     control     -> | "return" "~(" expression ")" 
#                    | "break" "~(" expression ")" 
#                    | "continue" "~(" expression ")" 
#                    | expression
#     expression  -> "#" STRING assignment | assignment
#     assignment  -> mapping "=" expression | mapping
#     mapping     -> disjunction "->" mapping | disjunction
#     disjunction -> conjunction ("or" conjunction)*
#     conjunction -> equality ("and" equality)*
#     equality    -> comparison (("=="|"!=") comparison)*
#     comparison  -> term (("<"|"<="|">"|">=") term)*
#     term        -> factor (("+"|"-") factor)*
#     factor      -> unary (("*"|"/"|"%") unary)*
#     unary       -> ("not"|"-") call | call "?" | call
#     call        -> primary ( "~(" arguments ")" | "." IDENTIFIER | "~[" expression "]" )*
#     arguments   -> expression ("," expression)*
#
#     primary     -> INTEGER | NUMBER | STRING | BOOLEAN | NULL | TYPE | array | map
#                    | function | target | ( "~(" | "(" ) expression ")"
#                    | block | conditional | while | for
#     array       -> "[" (expression ",")* "]"
#     map         -> "{" STRING ":" expression ",")* "}"
#     chunk       -> control*
#     block       -> "do" chunk "end"
#     conditional -> "if" expression "then" chunk
#                     ("elif" expression "then" chunk)*
#                     ("else" chunk)? "end"
#     while       -> "while" expression control
#     for         -> "for" expression "in" expression block
#     target      -> ID | declaration
#     declaration -> "let" ID
#     function    -> "function" "~(" parameters? ")" ("->" expression)? block
#     parameters  -> ID (":" expression)? ("," ID (":" expression)?)*
#
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

    # def check_if_map(self) -> bool:
    #     length = len(self.tokens)
    #     if self.current+2 < length:
    #         if self.tokens[self.current].ttype == TokenType.STRING and self.tokens[self.current+1].ttype == TokenType.COLON:
    #             return True
    #     return False

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
        self.lexer.report_error(token.line, token.col, "SYNTAX ERROR", msg)
        raise ast.SyntaxError(msg)

    def consume(self, ttype: TokenType, fail_msg: str) -> bool:
        if self.interactive and self.is_at_end():
            raise ast.IncompleteExpression()
        if self.is_at_end() or not self.check(ttype):
            self.error(self.peek(), fail_msg)
        return self.advance()

    def synchronize(self):
        line_before = self.peek().line
        while not self.is_at_end():
            self.advance()
            line_current = self.peek().line
            if not self.is_at_end() and line_before < line_current:
                return

    def any_type_terminal(self, line: int, col: int):
        return ast.Terminal(
            token=Token(
                ttype=TokenType.TYPE,
                literal="Any",
                line=line,
                col=col
            )
        )

    def null_terminal(self, line: int, col: int):
        return ast.Terminal(
            token=Token(
                ttype=TokenType.NULL,
                literal="null",
                line=line,
                col=col
            )
        )

    def parse_program(self):
        program = []
        contains_error = False
        while not self.is_at_end():
            try:
                expression = self.parse_control()
                # self.consume(TokenType.SEMICOLON, "Expected ';' after expression.")
                program.append(expression)
            except ast.SyntaxError as e:
                self.synchronize()
                contains_error = e
        self.advance()
        if contains_error:
            raise ast.SyntaxError("The code contains errors.")
        return ast.Program(program=program)

    def parse_control(self):
        if self.match([TokenType.RETURN, TokenType.BREAK, TokenType.CONTINUE]):
            operator = self.previous()
            self.consume(TokenType.CLROUND, f"Expected '(' after '{operator.literal}'.")
            expr = self.parse_expression()
            self.consume(TokenType.RROUND, f"Expected closing ')' after expression.")
            return ast.Unary(operator=operator, expr=expr)
        return self.parse_expression()

    def parse_expression(self):
        if self.match([TokenType.HASH]):
            operator = self.previous()
            self.consume(TokenType.STRING, "Expected a string annotation after '#'.")
            comment = self.previous()
            expr = self.parse_assignment()
            return ast.Annotation(operator=operator, comment=comment, expr=expr)
        return self.parse_assignment()

    def parse_assignment(self):
        mapping = self.parse_mapping()
        if self.match([TokenType.ASSIGN]):
            operator = self.previous()
            expr = self.parse_expression()
            if isinstance(mapping, ast.Terminal) and mapping.token.ttype == TokenType.ID:
                return ast.Assign(target=mapping, operator=operator, expr=expr)
            elif isinstance(mapping, ast.Declaration):
                return ast.Assign(target=mapping, operator=operator, expr=expr)
            elif isinstance(mapping, ast.Get):
                setter = ast.Set(operator=mapping.operator,
                                 expr=mapping.expr,
                                 index=mapping.index)
                return ast.Assign(target=setter, operator=operator, expr=expr)
            elif isinstance(mapping, ast.Array):
                print("here!")
                return ast.Assign(target=mapping, operator=operator, expr=expr)
            elif isinstance(mapping, ast.Map):
                return ast.Assign(target=mapping, operator=operator, expr=expr)
            self.error(operator, "Invalid assignment target.")
        return mapping

    def parse_mapping(self):
        disjunction = self.parse_disjunction()
        if self.match([TokenType.ARROW]):
            operator = self.previous()
            mapping = self.parse_mapping()
            if isinstance(mapping, ast.Grouping):
                mapping = mapping.expr
            return ast.Binary(left=disjunction, operator=operator, right=mapping)
        return disjunction

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
        call = self.parse_call()
        if self.match([TokenType.QUESTION]):
            op = self.previous()
            return ast.Unary(operator=op, expr=call)
        return call

    def parse_call(self):
        primary = self.parse_primary()
        while self.match([TokenType.CLROUND, TokenType.PERIOD, TokenType.CLSQUARE]):
            operator = self.previous()
            if operator.ttype == TokenType.CLROUND:
                arguments = self.parse_arguments()
                self.consume(TokenType.RROUND,
                             "Expected ')' to close argument list.")
                primary = ast.Call(expr=primary, operator=operator,
                                   arguments=arguments)
            elif operator.ttype == TokenType.CLSQUARE:
                index = self.parse_expression()
                primary = ast.Get(operator=operator, expr=primary, index=index)
                self.consume(TokenType.RSQUARE, "Expected closing ']'.")
            else:
                if self.match([TokenType.ID, TokenType.STRING]):
                    # Syntax sugar: a.field => a."field"
                    token = self.previous()
                    token.ttype = TokenType.STRING
                    index = ast.Terminal(token=token)
                    primary = ast.Get(operator=operator, expr=primary, index=index)
                else:
                    self.error(operator, "Expected a property name.")
        return primary

    def parse_primary(self):
        # print(f"parse_primary: next token = {self.peek()}")
        if self.match([TokenType.ID, TokenType.INTEGER, TokenType.NUMBER, TokenType.STRING, TokenType.BOOLEAN, TokenType.NULL, TokenType.TYPE]):
            token = self.previous()
            return ast.Terminal(token=token)
        if self.check(TokenType.LSQUARE):
            return self.parse_array()
        if self.check(TokenType.LCURLY):
            return self.parse_map()
        if self.check(TokenType.DO):
            return self.parse_block()
        if self.check(TokenType.IF):
            return self.parse_conditional()
        if self.check(TokenType.FOR):
            return self.parse_for()
        if self.check(TokenType.FUNCTION):
            return self.parse_function()
        if self.match([TokenType.LROUND, TokenType.CLROUND]):
            expr = self.parse_expression()
            self.consume(TokenType.RROUND, "Expected ')' after expression.")
            return ast.Grouping(expr=expr)
        if self.check(TokenType.ID) or self.check(TokenType.LET):
            return self.parse_target()
        if self.check(TokenType.TYPE):
            return self.parse_type_declaration()
        if self.peek().ttype in [TokenType.RETURN, TokenType.BREAK, TokenType.CONTINUE]:
            self.error(self.peek(), f"Invalid '{self.peek().literal}' expression.")
        # Only in interactive mode: Expected a missing expression.
        if self.interactive:
            raise ast.IncompleteExpression()
        self.error(self.peek(), "Expected an expression.")

    def parse_array(self):
        array = []
        if self.match([TokenType.LSQUARE]):
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

    def parse_map(self):
        dictionary = {}
        self.consume(TokenType.LCURLY, "Expected opening '{'.")
        if self.match([TokenType.RCURLY]):
            return ast.Map(map={})
        self.consume(TokenType.STRING, "Expected a member key.")
        token = self.previous()
        self.consume(TokenType.COLON, "Expected ':' after member key.")
        dictionary[token.literal] = self.parse_expression()
        while self.match([TokenType.COMMA]):
            self.consume(TokenType.STRING, "Expected a member key after a comma.")
            token = self.previous()
            self.consume(TokenType.COLON, "Expected ':' after member key.")
            dictionary[token.literal] = self.parse_expression()
        self.consume(TokenType.RCURLY,
                     "Expected closing '}' after list of members.")
        return ast.Map(map=dictionary)


    def parse_chunk_until(self, ends: List[Token]):
        exprs = []
        while self.peek().ttype not in ends:
            expr = self.parse_control()
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
            chunk = self.parse_chunk_until([TokenType.END, TokenType.ELIF, TokenType.ELSE])
            exprs.append(chunk)
            while self.match([TokenType.ELIF]):
                operators.append(self.previous())
                cond = self.parse_expression()
                conds.append(cond)
                self.consume(TokenType.THEN, "Expected 'then' after condition.")
                chunk = self.parse_chunk_until([TokenType.END, TokenType.ELIF, TokenType.ELSE])
                exprs.append(chunk)
            if self.match([TokenType.ELSE]):
                default = self.parse_chunk_until([TokenType.END])
            self.consume(TokenType.END, "Expected closing 'end' after conditional expression.")
            return ast.Conditional(operators=operators, conds=conds, exprs=exprs, default=default)

    def parse_for(self):
        if self.match([TokenType.FOR]):
            operator = self.previous()
            target = self.parse_expression()
            self.consume(TokenType.IN, "Expected 'in' keyword.")
            iterator = self.parse_expression()
            expr = self.parse_block()
            return ast.For(operator=operator, target=target, iterator=iterator, expr=expr)

    def parse_arguments(self):
        if self.check(TokenType.RROUND):
            return []
        expression = self.parse_expression()
        arguments = [expression]
        while self.match([TokenType.COMMA]):
            expression = self.parse_expression()
            arguments.append(expression)
        return arguments

    def parse_function(self):
        if self.match([TokenType.FUNCTION]):
            operator = self.previous()
            self.consume(TokenType.CLROUND, "Expected '(' after 'function' keyword.")
            parameters, param_types = self.parse_parameters()
            self.consume(
                TokenType.RROUND, "Expected closing ')' after list of function parameters.")
            out_type = self.parse_expression() if self.match(
                [TokenType.ARROW]) else self.any_type_terminal(operator.line, operator.col)
            # print(f"parse_function: out_type = {out_type}")
            expr = self.parse_block()
            return ast.Function(operator=operator, parameters=parameters, param_types=param_types, expr=expr, out_type=out_type)

    def parse_parameters(self):
        parameters = []
        param_types = []
        if self.match([TokenType.ID]):
            param = self.previous()
            param_type = self.parse_expression() if self.match(
                [TokenType.COLON]) else self.any_type_terminal(param.line, param.col)
            parameters.append(param)
            param_types.append(param_type)
            while self.match([TokenType.COMMA]):
                param = self.advance()
                if param.ttype != TokenType.ID:
                    self.error(param, "Expected an identifier.")
                param_type = self.parse_expression() if self.match(
                    [TokenType.COLON]) else self.any_type_terminal(param.line, param.col)
                parameters.append(param)
                param_types.append(param_type)
        return parameters, param_types

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

    def parse(self, code: str):
        self.reset()

        # Scan and parse.
        tree = None
        previous_lexer = copy.deepcopy(self.lexer)

        try:
            tokens = self.lexer.scan(code)
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
            raise(e)

        return tree
