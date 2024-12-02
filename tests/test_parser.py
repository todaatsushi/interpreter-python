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
