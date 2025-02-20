import pytest
import mindscript.ast as ast
from mindscript.parser import Parser

# 1. Test parsing a simple integer literal.
def test_parse_integer():
    parser = Parser()
    tree = parser.parse("42", "test_buffer")
    assert isinstance(tree, ast.Program)
    expr = tree.program[0]
    assert isinstance(expr, ast.Terminal)
    assert expr.token.literal == 42

# 2. Test parsing a simple string literal.
def test_parse_string():
    parser = Parser()
    tree = parser.parse('"hello"', "test_buffer")
    expr = tree.program[0]
    assert isinstance(expr, ast.Terminal)
    assert expr.token.literal == "hello"

# 3. Test parsing a binary addition expression.
def test_parse_addition():
    parser = Parser()
    tree = parser.parse("1 + 2", "test_buffer")
    expr = tree.program[0]
    # Expect a Binary node: 1 + 2
    assert isinstance(expr, ast.Binary)
    assert expr.operator.literal == "+"
    assert expr.left.token.literal == 1
    assert expr.right.token.literal == 2

# 4. Test parsing an assignment.
def test_parse_assignment():
    parser = Parser()
    tree = parser.parse("a = 3", "test_buffer")
    expr = tree.program[0]
    # Expect an Assign node whose target is a Terminal with id "a"
    assert isinstance(expr, ast.Assign)
    assert expr.target.token.literal == "a"
    assert expr.expr.token.literal == 3

# 5. Test parsing a conditional (if) expression.
def test_parse_conditional():
    parser = Parser()
    # Code: if 1 then do 2 end
    tree = parser.parse("if 1 do 2 end", "test_buffer")
    expr = tree.program[0]
    assert isinstance(expr, ast.Conditional)
    # There should be one condition.
    assert len(expr.conds) == 1
    # The then–clause is a block whose first expression is terminal 2.
    block = expr.exprs[0]
    assert isinstance(block, ast.Block)
    inner_expr = block.exprs[0]
    assert inner_expr.token.literal == 2

# 6. Test parsing a function definition.
def test_parse_function():
    parser = Parser()
    # Code: fun ~( ) -> Any do 1 end
    tree = parser.parse("fun( ) -> Any do 1 end", "test_buffer")
    expr = tree.program[0]
    assert isinstance(expr, ast.Function)
    # With no parameters provided the parser creates a placeholder parameter.
    assert len(expr.parameters) == 1
    # The function body is a block whose first expression is terminal 1.
    block = expr.expr
    assert isinstance(block, ast.Block)
    inner_expr = block.exprs[0]
    assert inner_expr.token.literal == 1

# 7. Test parsing a for loop.
def test_parse_for_loop():
    parser = Parser()
    # Code: for a in b do 1 end
    tree = parser.parse("for a in b do 1 end", "test_buffer")
    expr = tree.program[0]
    assert isinstance(expr, ast.For)
    # Target should be "a" and iterator "b"
    assert expr.target.token.literal == "a"
    assert expr.iterator.token.literal == "b"

# 8. Test parsing a block.
def test_parse_block():
    parser = Parser()
    tree = parser.parse("do 1 end", "test_buffer")
    expr = tree.program[0]
    assert isinstance(expr, ast.Block)
    assert expr.exprs[0].token.literal == 1

# 9. Test parsing an array literal.
def test_parse_array():
    parser = Parser()
    tree = parser.parse("[1, 2, 3]", "test_buffer")
    expr = tree.program[0]
    assert isinstance(expr, ast.Array)
    assert len(expr.array) == 3
    literals = [item.token.literal for item in expr.array]
    assert literals == [1, 2, 3]

# 10. Test parsing a map literal.
def test_parse_map():
    parser = Parser()
    tree = parser.parse("{ a: 1, b: 2 }", "test_buffer")
    expr = tree.program[0]
    assert isinstance(expr, ast.Map)
    # Check that the keys "a" and "b" exist.
    assert "a" in expr.map and "b" in expr.map
    assert expr.map["a"].token.literal == 1
    assert expr.map["b"].token.literal == 2

# 11. Test parsing an annotation.
def test_parse_annotation():
    parser = Parser()
    # Code: #annot 5
    tree = parser.parse("# annotation \n 5", "test_buffer")
    expr = tree.program[0]
    assert isinstance(expr, ast.Annotation)
    # The annotation should hold "annot" as its literal.
    assert expr.annotation.literal == "annotation"
    # And the annotated expression should be the terminal 5.
    assert expr.expr.token.literal == 5

# 12. Test parsing a unary minus.
def test_parse_unary_minus():
    parser = Parser()
    tree = parser.parse("-3", "test_buffer")
    expr = tree.program[0]
    assert isinstance(expr, ast.Unary)
    assert expr.operator.literal == "-"
    assert expr.expr.token.literal == 3

# 13. Test parsing a unary not.
def test_parse_unary_not():
    parser = Parser()
    tree = parser.parse("not true", "test_buffer")
    expr = tree.program[0]
    assert isinstance(expr, ast.Unary)
    assert expr.operator.literal == "not"
    assert expr.expr.token.literal is True

# 14. Test parsing a call expression.
def test_parse_call():
    parser = Parser()
    # Code: f~(1) is parsed as a call of function "f" with argument 1.
    tree = parser.parse("f(1)", "test_buffer")
    expr = tree.program[0]
    assert isinstance(expr, ast.Call)
    # The callee should be a Terminal with literal "f".
    assert expr.expr.token.literal == "f"
    # There should be one argument: terminal 1.
    assert len(expr.arguments) == 1
    assert expr.arguments[0].token.literal == 1

# 15. Test parsing a grouping expression.
def test_parse_grouping():
    parser = Parser()
    tree = parser.parse("(1 + 2)", "test_buffer")
    expr = tree.program[0]
    assert isinstance(expr, ast.Grouping)
    # The grouped expression is a binary expression.
    inner = expr.expr
    assert isinstance(inner, ast.Binary)

# 16. Test parsing a type definition.
def test_parse_type_definition():
    parser = Parser()
    # The lexer maps the keyword "type" to TYPECONS.
    tree = parser.parse("type Int", "test_buffer")
    expr = tree.program[0]
    assert isinstance(expr, ast.TypeDefinition)

# 17. Test parsing a map with an annotated key.
def test_parse_map_with_annotation():
    parser = Parser()
    # Code: { #ann a: 1 }
    tree = parser.parse("{ #ann \n a: 1 }", "test_buffer")
    expr = tree.program[0]
    assert isinstance(expr, ast.Map)
    # The value for key "a" should be an Annotation node.
    node = expr.map["a"]
    assert isinstance(node, ast.Annotation)
    assert node.annotation.literal == "ann"
    assert node.expr.token.literal == 1

# 18. Test parsing property access (object get).
def test_parse_object_get():
    parser = Parser()
    # Code: a.b  should yield an ObjectGet node.
    tree = parser.parse("a.b", "test_buffer")
    expr = tree.program[0]
    assert isinstance(expr, ast.ObjectGet)
    # The base expression is "a"
    assert expr.expr.token.literal == "a"
    # The property (as a terminal with a string token) is "b"
    assert expr.index.token.literal == "b"

# 19. Test that a syntax error is raised on invalid input.
def test_syntax_error():
    parser = Parser()
    # Test various syntax errors
    assert parser.parse("1 + + 3", "test_buffer") == None
    assert parser.parse(")", "test_buffer") == None
    assert parser.parse("oracle ()", "test_buffer") == None
    assert parser.parse("fun() -> do", "test_buffer") == None

# 20. Test that an incomplete expression raises an exception in interactive mode.
def test_incomplete_expression_interactive():
    parser = Parser(interactive=True)
    # Code with an incomplete block (missing "end")
    with pytest.raises(ast.IncompleteExpression):
        parser.parse("do 1", "test_buffer")
