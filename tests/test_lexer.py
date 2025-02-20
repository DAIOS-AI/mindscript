import pytest
from mindscript.ast import TokenType, LexicalError, IncompleteExpression
from mindscript.lexer import Lexer  # Adjust the import path as needed

def test_integer():
    lexer = Lexer()
    tokens = lexer.scan("123", "test_stream")
    # The last token is EOF; check the first token
    int_token = tokens[0]
    assert int_token.ttype == TokenType.INTEGER
    assert int_token.literal == 123

def test_float():
    lexer = Lexer()
    tokens = lexer.scan("3.14", "test_stream")
    number_token = tokens[0]
    assert number_token.ttype == TokenType.NUMBER
    # Floating point precision might be an issue;
    # you can use pytest.approx for comparison if necessary.
    assert number_token.literal == pytest.approx(3.14)

def test_string_single_quotes():
    lexer = Lexer()
    tokens = lexer.scan("'hello'", "test_stream")
    str_token = tokens[0]
    assert str_token.ttype == TokenType.STRING
    assert str_token.literal == "hello"

def test_string_double_quotes():
    lexer = Lexer()
    tokens = lexer.scan('"world"', "test_stream")
    str_token = tokens[0]
    assert str_token.ttype == TokenType.STRING
    assert str_token.literal == "world"

def test_keyword_boolean():
    lexer = Lexer()
    tokens = lexer.scan("true false", "test_stream")
    token_true, token_false, _ = tokens
    assert token_true.ttype == TokenType.BOOLEAN
    assert token_true.literal is True
    assert token_false.ttype == TokenType.BOOLEAN
    assert token_false.literal is False

def test_identifier():
    lexer = Lexer()
    tokens = lexer.scan("variableName", "test_stream")
    id_token = tokens[0]
    assert id_token.ttype == TokenType.ID
    assert id_token.literal == "variableName"

def test_parens_and_brackets():
    lexer = Lexer()
    # Test a small expression with different brackets and punctuation.
    code = " ( ) [ ] { }"
    tokens = lexer.scan(code, "test_stream")
    # Expected order: LROUND, RROUND, LSQUARE, RSQUARE, LCURLY, RCURLY, EOF
    expected_types = [
        TokenType.LROUND,
        TokenType.RROUND,
        TokenType.LSQUARE,
        TokenType.RSQUARE,
        TokenType.LCURLY,
        TokenType.RCURLY,
        TokenType.EOF,
    ]
    for token, expected in zip(tokens, expected_types):
        assert token.ttype == expected

def test_closed_parens():
    lexer = Lexer()
    # Test a small expression with different brackets and punctuation.
    code = "hello( )"
    tokens = lexer.scan(code, "test_stream")
    # Expected order: ID, CLROUND, RROUND, EOF
    expected_types = [
        TokenType.ID,
        TokenType.CLROUND,
        TokenType.RROUND,
        TokenType.EOF,
    ]
    for token, expected in zip(tokens, expected_types):
        assert token.ttype == expected


def test_arrow_and_comparison():
    lexer = Lexer()
    # Test tokens for '->', '==', '!=' etc.
    code = "-> == != <= >= < >"
    tokens = lexer.scan(code, "test_stream")
    expected_types = [
        TokenType.ARROW,
        TokenType.EQ,
        TokenType.NEQ,
        TokenType.LESS_EQ,
        TokenType.GREATER_EQ,
        TokenType.LESS,
        TokenType.GREATER,
        TokenType.EOF
    ]
    for token, expected in zip(tokens, expected_types):
        assert token.ttype == expected

def test_annotation():
    lexer = Lexer()
    # This example assumes that a '#' starts an annotation.
    code = "# This is a comment\nvariable"
    tokens = lexer.scan(code, "test_stream")
    # Depending on the implementation, the annotation might be returned as a HASH token or a NULL token.
    # Here we expect the first token to be a HASH (if non-empty) and the second to be the identifier.
    hash_token = tokens[0]
    id_token = tokens[1]
    # If the annotation scanning returns a value, then token type should be HASH.
    if hash_token.literal is not None:
        assert hash_token.ttype == TokenType.HASH
    else:
        assert hash_token.ttype == TokenType.NULL
    assert id_token.ttype == TokenType.ID
    assert id_token.literal == "variable"

def test_unterminated_string():
    lexer = Lexer()
    # Expect the lexer to raise a LexicalError when encountering an unterminated string.
    with pytest.raises(LexicalError):
        lexer.scan("'unterminated", "test_stream")

def test_unexpected_character():
    lexer = Lexer()
    # The '@' character is not handled, so it should raise a LexicalError.
    with pytest.raises(LexicalError):
        lexer.scan("@", "test_stream")
