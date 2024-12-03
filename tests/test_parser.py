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
            ("let 5;", ["Expected IDENTIFIER, got INT at position 5."]),
            ("let variable 5;", ["Expected =, got INT at position 14."]),
        )

        for code, expected in test_cases:
            lexer = lexers.Lexer.new(code)
            parser = parsers.Parser.new(lexer)

            parser.parse_program()

            self.assertEqual(len(parser.errors), len(expected))
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

        expected = "let myVar = anotherVar;\n"
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
