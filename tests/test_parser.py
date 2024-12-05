import unittest

from interpreter import lexers, parsers, tokens
from interpreter import ast
from tests import utils


class TestParser(unittest.TestCase):
    def test_new_parser_sets_tokens(self) -> None:
        program_input = "let x = 5;"
        lexer = lexers.Lexer.new(program_input)
        parser = parsers.Parser.new(lexer)

        self.assertEqual(
            parser.current_token,
            tokens.Token(type=tokens.TokenType.LET, value="let".encode("ascii")),
        )
        self.assertEqual(
            parser.peek_token,
            tokens.Token(type=tokens.TokenType.IDENTIFIER, value="x".encode("ascii")),
        )

    def test_next_token(self) -> None:
        program_input = "let x = 5;"
        lexer = lexers.Lexer.new(program_input)

        parser = parsers.Parser.new(lexer)
        parser.next_token()

        self.assertEqual(
            parser.current_token,
            tokens.Token(type=tokens.TokenType.IDENTIFIER, value="x".encode("ascii")),
        )
        self.assertEqual(
            parser.peek_token,
            tokens.Token(type=tokens.TokenType.ASSIGN, value="=".encode("ascii")),
        )


class TestParseProgram(unittest.TestCase):
    def test_parses_let(self) -> None:
        script = utils.read_script("tests/fixtures/02.mky")
        lexer = lexers.Lexer.new(script)
        parser = parsers.Parser.new(lexer)

        program = parser.parse_program()

        self.assertEqual(len(program.statements), 3)

        test_cases: tuple[str, ...] = ("x", "y", "foobar")

        for i, tc in enumerate(test_cases):
            with self.subTest(f"Identifier: {tc}"):
                statement = program.statements[i]

                self.assertEqual(statement.token_literal(), "let")

                self.assertIsInstance(statement, ast.Let)
                assert isinstance(statement, ast.Let)

                self.assertEqual(statement.name.value, tc)
                self.assertEqual(statement.name.token_literal(), tc)

    def test_parse_error(self) -> None:
        test_cases: tuple[tuple[str, list[str]], ...] = (
            (
                "let 5;",
                ["Expected IDENTIFIER, got INT at position 5."],
            ),
            (
                "let variable 5;",
                ["Expected =, got INT at position 14."],
            ),
        )

        for code, expected in test_cases:
            lexer = lexers.Lexer.new(code)
            parser = parsers.Parser.new(lexer)

            parser.parse_program()

            self.assertEqual(
                len(parser.errors), len(expected), f"{parser.errors} vs {expected}"
            )
            for i, err in enumerate(parser.errors):
                self.assertEqual(err, expected[i])

    def test_parses_return(self) -> None:
        script = utils.read_script("tests/fixtures/03.mky")
        lexer = lexers.Lexer.new(script)
        parser = parsers.Parser.new(lexer)

        program = parser.parse_program()

        self.assertEqual(len(program.statements), 3)

        test_cases: tuple[str, ...] = ("5", "10", "993322")

        for i, tc in enumerate(test_cases):
            with self.subTest(f"Identifier: {tc}"):
                statement = program.statements[i]

                self.assertEqual(statement.token_literal(), "return")
                self.assertIsInstance(statement, ast.Return)
                assert isinstance(statement, ast.Return)

    def test_string(self) -> None:
        program = ast.Program(
            statements=[
                ast.Let(
                    token=tokens.Token(
                        type=tokens.TokenType.LET,
                        value="let".encode("ascii"),
                    ),
                    name=ast.Identifier(
                        token=tokens.Token(
                            type=tokens.TokenType.IDENTIFIER,
                            value="myVar".encode("ascii"),
                        ),
                        value="myVar",
                    ),
                    value=ast.Identifier(
                        token=tokens.Token(
                            type=tokens.TokenType.IDENTIFIER,
                            value="anotherVar".encode("ascii"),
                        ),
                        value="anotherVar",
                    ),
                )
            ]
        )

        expected = "let myVar = anotherVar;"
        actual = str(program)

        self.assertEqual(expected, actual)

    def test_register(self) -> None:
        parser = parsers.Parser.new(lexers.Lexer.new("let x = 5;"))
        _let_expr = ast.Identifier(
            token=tokens.Token(type=tokens.TokenType.LET, value="let".encode("ascii")),
            value="let",
        )

        def valid_infix(expr: ast.Expression) -> ast.Expression:
            return _let_expr

        def valid_prefix() -> ast.Expression:
            return _let_expr

        with self.subTest("Register valid infix"):
            parser.register_infix(tokens.TokenType.LET, func=valid_infix)
            self.assertEqual(
                parser.parse_functions["INFIX"][tokens.TokenType.LET], valid_infix
            )

        with self.subTest("Register valid prefix"):
            parser.register_prefix(tokens.TokenType.LET, func=valid_prefix)
            self.assertEqual(
                parser.parse_functions["PREFIX"][tokens.TokenType.LET], valid_prefix
            )

    def test_parse_boolean_expression(self) -> None:
        test_cases: tuple[tuple[str, bool], ...] = (("true;", True), ("false;", False))
        for code, expected in test_cases:
            lexer = lexers.Lexer.new(code)
            parser = parsers.Parser.new(lexer)
            program = parser.parse_program()

            with self.subTest("Program has 1 statement"):
                self.assertEqual(len(program.statements), 1)
                self.assertEqual(len(parser.errors), 0, f"Errors: {parser.errors}")

            with self.subTest("Statement is expression statement"):
                statement = program.statements[0]
                self.assertIsInstance(statement, ast.ExpressionStatement)
                assert isinstance(statement, ast.ExpressionStatement)

            with self.subTest("Statement expression is identifier"):
                identifier = statement.expression
                self.assertIsInstance(identifier, ast.BooleanLiteral)
                assert isinstance(identifier, ast.BooleanLiteral)

            with self.subTest("Identifier is true"):
                self.assertEqual(identifier.value, expected)
                self.assertEqual(identifier.token_literal(), str(expected).lower())

    def test_parse_identifier_expression(self) -> None:
        code = "foobar;"
        lexer = lexers.Lexer.new(code)
        parser = parsers.Parser.new(lexer)

        program = parser.parse_program()

        with self.subTest("Program has 1 statement"):
            self.assertEqual(len(program.statements), 1)
            self.assertEqual(len(parser.errors), 0)

        with self.subTest("Statement is expression statement"):
            statement = program.statements[0]
            self.assertIsInstance(statement, ast.ExpressionStatement)
            assert isinstance(statement, ast.ExpressionStatement)

        with self.subTest("Statement expression is identifier"):
            identifier = statement.expression
            self.assertIsInstance(identifier, ast.Identifier)
            assert isinstance(identifier, ast.Identifier)

        with self.subTest("Identifier is foobar"):
            self.assertEqual(identifier.value, "foobar")
            self.assertEqual(identifier.token_literal(), "foobar")

    def test_parse_integer_expression(self) -> None:
        code = "5;"
        lexer = lexers.Lexer.new(code)
        parser = parsers.Parser.new(lexer)

        program = parser.parse_program()

        with self.subTest("Program has 1 statement"):
            self.assertEqual(len(program.statements), 1)
            self.assertEqual(len(parser.errors), 0)

        with self.subTest("Statement is expression statement"):
            statement = program.statements[0]
            self.assertIsInstance(statement, ast.ExpressionStatement)
            assert isinstance(statement, ast.ExpressionStatement)

        with self.subTest("Statement expression is identifier"):
            identifier = statement.expression
            self.assertIsInstance(identifier, ast.IntegerLiteral)
            assert isinstance(identifier, ast.IntegerLiteral)

        with self.subTest("Identifier is 5"):
            self.assertEqual(identifier.value, 5)
            self.assertEqual(identifier.token_literal(), "5")

    def test_parses_prefix_expressions(self) -> None:
        test_cases: tuple[tuple[str, str, int, type[ast.Expression]], ...] = (
            ("!5;", "!", 5, ast.IntegerLiteral),
            ("-15;", "-", 15, ast.IntegerLiteral),
            ("!true", "!", True, ast.BooleanLiteral),
            ("!false", "!", False, ast.BooleanLiteral),
        )

        for code, prefix_operator, operated_value, expected_class in test_cases:
            lexer = lexers.Lexer.new(code)
            parser = parsers.Parser.new(lexer)

            program = parser.parse_program()

            with self.subTest(f"Prefix for code: {code}"):
                with self.subTest(f"Number of statements for {code}"):
                    self.assertEqual(len(program.statements), 1)

                self.assertEqual(
                    len(parser.errors),
                    0,
                    msg=f"Errors found when parsing '{code}': {parser.errors}",
                )

                statement = program.statements[0]
                with self.subTest(f"Is expression statement: {code}"):
                    self.assertIsInstance(statement, ast.ExpressionStatement)
                    assert isinstance(statement, ast.ExpressionStatement)

                prefix_expression = statement.expression
                with self.subTest(f"Is prefix expression: {code}"):
                    self.assertIsInstance(prefix_expression, ast.Prefix)
                    assert isinstance(prefix_expression, ast.Prefix)

                with self.subTest(
                    f"Prefix expression operator: {code} - {prefix_operator}"
                ):
                    self.assertEqual(prefix_expression.operator, prefix_operator)

                with self.subTest(
                    f"Prefix expression value: {code} - {operated_value}"
                ):
                    self.assertIsInstance(prefix_expression.right, expected_class)
                    assert isinstance(prefix_expression.right, expected_class)
                    self.assertEqual(prefix_expression.right.value, operated_value)
                    self.assertEqual(
                        prefix_expression.right.token_literal(),
                        str(operated_value).lower(),
                    )

    def test_parses_infix_expressions(self) -> None:
        test_cases: tuple[
            tuple[str, object, str, object, type[ast.Expression], type[ast.Expression]],
            ...,
        ] = (
            ("5 + 5;", 5, "+", 5, ast.IntegerLiteral, ast.IntegerLiteral),
            ("5 - 5;", 5, "-", 5, ast.IntegerLiteral, ast.IntegerLiteral),
            ("5 * 5;", 5, "*", 5, ast.IntegerLiteral, ast.IntegerLiteral),
            ("5 / 5;", 5, "/", 5, ast.IntegerLiteral, ast.IntegerLiteral),
            ("5 > 5;", 5, ">", 5, ast.IntegerLiteral, ast.IntegerLiteral),
            ("5 < 5;", 5, "<", 5, ast.IntegerLiteral, ast.IntegerLiteral),
            ("5 == 5;", 5, "==", 5, ast.IntegerLiteral, ast.IntegerLiteral),
            ("5 != 5;", 5, "!=", 5, ast.IntegerLiteral, ast.IntegerLiteral),
            (
                "foobar + barfoo;",
                "foobar",
                "+",
                "barfoo",
                ast.Identifier,
                ast.Identifier,
            ),
            (
                "foobar - barfoo;",
                "foobar",
                "-",
                "barfoo",
                ast.Identifier,
                ast.Identifier,
            ),
            (
                "foobar * barfoo;",
                "foobar",
                "*",
                "barfoo",
                ast.Identifier,
                ast.Identifier,
            ),
            (
                "foobar / barfoo;",
                "foobar",
                "/",
                "barfoo",
                ast.Identifier,
                ast.Identifier,
            ),
            (
                "foobar > barfoo;",
                "foobar",
                ">",
                "barfoo",
                ast.Identifier,
                ast.Identifier,
            ),
            (
                "foobar < barfoo;",
                "foobar",
                "<",
                "barfoo",
                ast.Identifier,
                ast.Identifier,
            ),
            (
                "foobar == barfoo;",
                "foobar",
                "==",
                "barfoo",
                ast.Identifier,
                ast.Identifier,
            ),
            (
                "foobar != barfoo;",
                "foobar",
                "!=",
                "barfoo",
                ast.Identifier,
                ast.Identifier,
            ),
            ("true == true", True, "==", True, ast.BooleanLiteral, ast.BooleanLiteral),
            (
                "true != false",
                True,
                "!=",
                False,
                ast.BooleanLiteral,
                ast.BooleanLiteral,
            ),
            (
                "false == false",
                False,
                "==",
                False,
                ast.BooleanLiteral,
                ast.BooleanLiteral,
            ),
        )

        for (
            code,
            expected_left,
            expected_operator,
            expected_right,
            expected_class_left,
            expected_class_right,
        ) in test_cases:
            lexer = lexers.Lexer.new(code)
            parser = parsers.Parser.new(lexer)

            program = parser.parse_program()

            with self.subTest(f"Infix for code: {code}"):
                with self.subTest(f"Number of statements for {code}"):
                    self.assertEqual(len(program.statements), 1)

                statement = program.statements[0]
                with self.subTest(f"Is expression statement: {code}"):
                    self.assertIsInstance(statement, ast.ExpressionStatement)
                    assert isinstance(statement, ast.ExpressionStatement)

                infix_expression = statement.expression
                with self.subTest(f"Is infix expression: {code}"):
                    self.assertIsInstance(infix_expression, ast.Infix)
                    assert isinstance(infix_expression, ast.Infix)

                with self.subTest(f"Operator is {expected_operator}"):
                    self.assertEqual(infix_expression.operator, expected_operator)
                    self.assertEqual(
                        infix_expression.token,
                        tokens.Token(
                            type=tokens.TokenType(expected_operator),
                            value=expected_operator.encode("ascii"),
                        ),
                    )

                actual_left = infix_expression.left
                with self.subTest(f"Test left is correct literal: {code}"):
                    self.assertIsInstance(actual_left, expected_class_left)
                    assert isinstance(actual_left, expected_class_left)

                    self.assertEqual(expected_left, actual_left.value)

                actual_right = infix_expression.right
                with self.subTest(f"Test right is correct literal: {code}"):
                    self.assertIsInstance(actual_right, expected_class_right)
                    assert isinstance(actual_right, expected_class_right)

                    self.assertEqual(expected_right, actual_right.value)

    def test_parses_if_expression(self) -> None:
        test_cases: tuple[tuple[str, bool], ...] = (
            ("if (x < y) { x } else { y }", True),
            # ("if (x < y) { x }", False),
        )

        for code, has_alt in test_cases:
            lexer = lexers.Lexer.new(code)
            parser = parsers.Parser.new(lexer)

            program = parser.parse_program()

            with self.subTest(f"No errors for {code}"):
                self.assertEqual(
                    len(parser.errors), 0, f"Errors found: {parser.errors}"
                )

            with self.subTest(f"Number of statements for {code}"):
                self.assertEqual(len(program.statements), 1)

            statement = program.statements[0]
            with self.subTest(f"Is expression statement: {code}"):
                self.assertIsInstance(statement, ast.ExpressionStatement)
                assert isinstance(statement, ast.ExpressionStatement)

            if_expression = statement.expression
            with self.subTest(f"Is infix expression: {code}"):
                self.assertIsInstance(if_expression, ast.If)
                assert isinstance(if_expression, ast.If)

            infix = if_expression.condition
            with self.subTest(f"Condition is infix: {code}"):
                self.assertIsInstance(infix, ast.Infix)
                assert isinstance(infix, ast.Infix)

                self.assertEqual(
                    infix.left,
                    ast.Identifier(
                        token=tokens.Token(
                            value=b"x", type=tokens.TokenType.IDENTIFIER
                        ),
                        value="x",
                    ),
                )

                self.assertEqual(
                    infix.right,
                    ast.Identifier(
                        token=tokens.Token(
                            value=b"y", type=tokens.TokenType.IDENTIFIER
                        ),
                        value="y",
                    ),
                )

                self.assertEqual(infix.operator, "<")
                self.assertEqual(
                    infix.token,
                    tokens.Token(value=b"<", type=tokens.TokenType.LESS_THAN),
                )

            consequence = if_expression.consequence
            with self.subTest(f"Consequence for {code}"):
                self.assertIsInstance(consequence, ast.BlockStatement)
                assert isinstance(consequence, ast.BlockStatement)

                self.assertEqual(len(consequence.statements), 1)

                expression = consequence.statements[0]
                self.assertIsInstance(expression, ast.ExpressionStatement)
                assert isinstance(expression, ast.ExpressionStatement)

                self.assertEqual(
                    expression.token,
                    tokens.Token(value=b"x", type=tokens.TokenType.IDENTIFIER),
                )
                self.assertIsNotNone(expression.expression)

            alternative = if_expression.alternative
            if has_alt:
                with self.subTest(f"Alternative for {code}"):
                    self.assertIsInstance(alternative, ast.BlockStatement)
                    assert isinstance(alternative, ast.BlockStatement)

                    self.assertEqual(len(alternative.statements), 1)

                    expression = alternative.statements[0]
                    self.assertIsInstance(expression, ast.ExpressionStatement)
                    assert isinstance(expression, ast.ExpressionStatement)

                    self.assertEqual(
                        expression.token,
                        tokens.Token(value=b"y", type=tokens.TokenType.IDENTIFIER),
                    )
                    self.assertIsNotNone(expression.expression)


class TestOperatorPrecendenceParsing(unittest.TestCase):
    def test_operator_precedence_parsing(self) -> None:
        test_cases: tuple[tuple[str, str], ...] = (
            ("-a * b", "((-a) * b)"),
            ("!-a", "(!(-a))"),
            ("a + b + c", "((a + b) + c)"),
            ("a + b - c", "((a + b) - c)"),
            ("a * b * c", "((a * b) * c)"),
            ("a * b / c", "((a * b) / c)"),
            ("a + b / c", "(a + (b / c))"),
            ("a + b * c + d / e - f", "(((a + (b * c)) + (d / e)) - f)"),
            ("3 + 4; -5 * 5", "(3 + 4)((-5) * 5)"),
            ("5 > 4 == 3 < 4", "((5 > 4) == (3 < 4))"),
            ("5 < 4 != 3 > 4", "((5 < 4) != (3 > 4))"),
            ("3 + 4 * 5 == 3 * 1 + 4 * 5", "((3 + (4 * 5)) == ((3 * 1) + (4 * 5)))"),
            ("true", "true"),
            ("false", "false"),
            ("3 > 5 == false", "((3 > 5) == false)"),
            ("3 < 5 == true", "((3 < 5) == true)"),
            ("1 + (2 + 3) + 4", "((1 + (2 + 3)) + 4)"),
            ("(5 + 5) * 2", "((5 + 5) * 2)"),
            ("2 / (5 + 5)", "(2 / (5 + 5))"),
            ("-(5 + 5)", "(-(5 + 5))"),
            ("!(true == true)", "(!(true == true))"),
        )

        for code, expected in test_cases:
            lexer = lexers.Lexer.new(code)
            parser = parsers.Parser.new(lexer)

            program = parser.parse_program()
            with self.subTest(f"Check no errors for: {code}"):
                self.assertEqual(
                    len(parser.errors), 0, f"{len(parser.errors)} found for {code}"
                )

            with self.subTest(f"Parsed properly: {code}"):
                self.assertEqual(str(program), expected)
