import unittest

from monkey.interpreter import tokens as tk, lexers as lx

from tests import utils


class TestNextToken(unittest.TestCase):
    def test_read_char(self) -> None:
        lexer = lx.Lexer.new("a")
        self.assertEqual(lexer.position, 0)
        self.assertEqual(lexer.read_position, 1)
        self.assertEqual(lexer.literal, "a".encode("ascii"))

        lexer.read_char()
        self.assertEqual(lexer.position, 1)
        self.assertEqual(lexer.read_position, 2)
        self.assertEqual(lexer.literal, None)

    def test_parse_multi_tokens(self) -> None:
        test_cases: tuple[tuple[str, tk.TokenType], ...] = (
            ("==", tk.TokenType.EQUALS),
            ("!=", tk.TokenType.NOT_EQUALS),
        )

        for value, expected in test_cases:
            lexer = lx.Lexer.new(value)
            actual: tk.TokenType = lexer.next_token().type

            with self.subTest():
                self.assertEqual(actual, expected)

    def test_parse_keywords(self) -> None:
        test_cases: tuple[tuple[str, tk.TokenType], ...] = (
            ("let", tk.TokenType.LET),
            ("if", tk.TokenType.IF),
            ("else", tk.TokenType.ELSE),
            ("true", tk.TokenType.TRUE),
            ("false", tk.TokenType.FALSE),
            ("return", tk.TokenType.RETURN),
            ("variable", tk.TokenType.IDENTIFIER),
            ("fn", tk.TokenType.FUNCTION),
            ("10", tk.TokenType.INT),
        )

        for value, expected in test_cases:
            lexer = lx.Lexer.new(value)
            actual: tk.TokenType = lexer.next_token().type

            with self.subTest():
                self.assertEqual(actual, expected)

    def test_parse_token(self) -> None:
        lexer = lx.Lexer.new("=+(){},;5-/*<>!")

        test_cases: tuple[tuple[str | None, tk.TokenType], ...] = (
            ("=", tk.TokenType.ASSIGN),
            ("+", tk.TokenType.PLUS),
            ("(", tk.TokenType.LEFT_PARENTHESES),
            (")", tk.TokenType.RIGHT_PARENTHESES),
            ("{", tk.TokenType.LEFT_BRACE),
            ("}", tk.TokenType.RIGHT_BRACE),
            (",", tk.TokenType.COMMA),
            (";", tk.TokenType.SEMICOLON),
            ("5", tk.TokenType.INT),
            ("-", tk.TokenType.MINUS),
            ("/", tk.TokenType.DIVIDE),
            ("*", tk.TokenType.MULTIPLY),
            ("<", tk.TokenType.LESS_THAN),
            (">", tk.TokenType.MORE_THAN),
            ("!", tk.TokenType.EXCLAIMATION_MARK),
            (None, tk.TokenType.EOF),
        )

        for expected_value, expected_type in test_cases:
            token: tk.Token = lexer.next_token()
            actual_value = token.value.decode("ascii") if token.value else token.value
            actual_type = token.type
            with self.subTest():
                self.assertEqual(
                    actual_value,
                    expected_value,
                    f"Expected '{expected_value}', got '{actual_value}'",
                )
                self.assertEqual(
                    actual_type,
                    expected_type,
                    f"Expected '{expected_type}', got '{actual_type}'",
                )

    def test_parses_string(self) -> None:
        code = '"test string"'
        lexer = lx.Lexer.new(code)

        token: tk.Token = lexer.next_token()

        self.assertIsNotNone(token.value)
        assert token.value is not None

        self.assertEqual(token.type, tk.TokenType.STRING)

        actual_value = token.value.decode("ascii")
        self.assertEqual(actual_value, "test string")

    def test_parses_script(self) -> None:
        input = utils.read_script("tests/fixtures/01.mky")
        lexer = lx.Lexer.new(input)

        test_cases: tuple[tuple[str | None, tk.TokenType], ...] = (
            # Line 1
            ("let", tk.TokenType.LET),
            ("five", tk.TokenType.IDENTIFIER),
            ("=", tk.TokenType.ASSIGN),
            ("5", tk.TokenType.INT),
            (";", tk.TokenType.SEMICOLON),
            # Line 2
            ("let", tk.TokenType.LET),
            ("ten", tk.TokenType.IDENTIFIER),
            ("=", tk.TokenType.ASSIGN),
            ("10", tk.TokenType.INT),
            (";", tk.TokenType.SEMICOLON),
            # Line 4-6
            ("let", tk.TokenType.LET),
            ("add", tk.TokenType.IDENTIFIER),
            ("=", tk.TokenType.ASSIGN),
            ("fn", tk.TokenType.FUNCTION),
            ("(", tk.TokenType.LEFT_PARENTHESES),
            ("x", tk.TokenType.IDENTIFIER),
            (",", tk.TokenType.COMMA),
            ("y", tk.TokenType.IDENTIFIER),
            (")", tk.TokenType.RIGHT_PARENTHESES),
            ("{", tk.TokenType.LEFT_BRACE),
            ("x", tk.TokenType.IDENTIFIER),
            ("+", tk.TokenType.PLUS),
            ("y", tk.TokenType.IDENTIFIER),
            (";", tk.TokenType.SEMICOLON),
            ("}", tk.TokenType.RIGHT_BRACE),
            (";", tk.TokenType.SEMICOLON),
            # Line 8
            ("let", tk.TokenType.LET),
            ("result", tk.TokenType.IDENTIFIER),
            ("=", tk.TokenType.ASSIGN),
            ("add", tk.TokenType.IDENTIFIER),
            ("(", tk.TokenType.LEFT_PARENTHESES),
            ("five", tk.TokenType.IDENTIFIER),
            (",", tk.TokenType.COMMA),
            ("ten", tk.TokenType.IDENTIFIER),
            (")", tk.TokenType.RIGHT_PARENTHESES),
            (";", tk.TokenType.SEMICOLON),
            # Line 9
            ("!", tk.TokenType.EXCLAIMATION_MARK),
            ("-", tk.TokenType.MINUS),
            ("/", tk.TokenType.DIVIDE),
            ("*", tk.TokenType.MULTIPLY),
            ("5", tk.TokenType.INT),
            (";", tk.TokenType.SEMICOLON),
            # Line 10
            ("5", tk.TokenType.INT),
            ("<", tk.TokenType.LESS_THAN),
            ("10", tk.TokenType.INT),
            (">", tk.TokenType.MORE_THAN),
            ("5", tk.TokenType.INT),
            (";", tk.TokenType.SEMICOLON),
            # Line 12
            ("if", tk.TokenType.IF),
            ("(", tk.TokenType.LEFT_PARENTHESES),
            ("5", tk.TokenType.INT),
            ("<", tk.TokenType.LESS_THAN),
            ("10", tk.TokenType.INT),
            (")", tk.TokenType.RIGHT_PARENTHESES),
            ("{", tk.TokenType.LEFT_BRACE),
            # Line 13
            ("return", tk.TokenType.RETURN),
            ("true", tk.TokenType.TRUE),
            (";", tk.TokenType.SEMICOLON),
            # Line 14
            ("}", tk.TokenType.RIGHT_BRACE),
            ("else", tk.TokenType.ELSE),
            ("{", tk.TokenType.LEFT_BRACE),
            # Line 15
            ("return", tk.TokenType.RETURN),
            ("false", tk.TokenType.FALSE),
            (";", tk.TokenType.SEMICOLON),
            # Line 16
            ("}", tk.TokenType.RIGHT_BRACE),
            # Line 18
            ("10", tk.TokenType.INT),
            ("==", tk.TokenType.EQUALS),
            ("10", tk.TokenType.INT),
            (";", tk.TokenType.SEMICOLON),
            # Line 18
            ("10", tk.TokenType.INT),
            ("!=", tk.TokenType.NOT_EQUALS),
            ("9", tk.TokenType.INT),
            (";", tk.TokenType.SEMICOLON),
            # Line 20
            ("foobar", tk.TokenType.STRING),
            # Line 21
            ("foo bar", tk.TokenType.STRING),
            # Line 22
            ("[", tk.TokenType.LEFT_SQUARE_BRACKET),
            ("1", tk.TokenType.INT),
            (",", tk.TokenType.COMMA),
            ("two", tk.TokenType.STRING),
            (",", tk.TokenType.COMMA),
            ("three", tk.TokenType.IDENTIFIER),
            ("]", tk.TokenType.RIGHT_SQUARE_BRACKET),
            (";", tk.TokenType.SEMICOLON),
            # Line 23
            ("{", tk.TokenType.LEFT_BRACE),
            ("hello", tk.TokenType.STRING),
            (":", tk.TokenType.COLON),
            ("world", tk.TokenType.STRING),
            ("}", tk.TokenType.RIGHT_BRACE),
            (";", tk.TokenType.SEMICOLON),
            # Line 24
            ("`", tk.TokenType.ILLEGAL),
            (None, tk.TokenType.EOF),
        )

        for expected_value, expected_type in test_cases:
            token: tk.Token = lexer.next_token()
            actual_value = token.value.decode("ascii") if token.value else token.value
            actual_type = token.type
            with self.subTest(f"Position: {lexer.position}"):
                self.assertEqual(
                    actual_value,
                    expected_value,
                    f"Expected '{expected_value}', got '{actual_value}'",
                )
                self.assertEqual(
                    actual_type,
                    expected_type,
                    f"Expected '{expected_type}', got '{actual_type}'",
                )
