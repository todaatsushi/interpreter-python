import unittest

from interpreter import tokens as tk, lexers as lx


class TestNextToken(unittest.TestCase):
    def test_read_char(self) -> None:
        lexer = lx.Lexer.new("a")
        self.assertEqual(lexer.position, 0)
        self.assertEqual(lexer.read_position, 1)
        self.assertEqual(lexer.char, "a".encode("ascii"))

        lexer.read_char()
        self.assertEqual(lexer.position, 1)
        self.assertEqual(lexer.read_position, 2)
        self.assertEqual(lexer.char, None)

    def test_read_token(self) -> None:
        test_cases: tuple[tuple[str, str], ...] = (
            ("+", "+"),
            ("0", "0"),
            ("let", "let"),
            ("l et", "l"),
        )
        for input, expected in test_cases:
            with self.subTest():
                lexer = lx.Lexer.new(input)
                actual = lexer.read_token()
                self.assertEqual(actual, expected)

    def test_parse_token(self) -> None:
        lexer = lx.Lexer.new("=+(){},;")

        test_cases: tuple[tuple[str | None, tk.TokenType], ...] = (
            ("=", tk.TokenType.ASSIGN),
            ("+", tk.TokenType.PLUS),
            ("(", tk.TokenType.LEFT_PARENTHESES),
            (")", tk.TokenType.RIGHT_PARENTHESES),
            ("{", tk.TokenType.LEFT_BRACE),
            ("}", tk.TokenType.RIGHT_BRACE),
            (",", tk.TokenType.COMMA),
            (";", tk.TokenType.SEMICOLON),
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
                    f"Expected '{expected_value}, got '{actual_value}'",
                )
                self.assertEqual(
                    actual_type,
                    expected_type,
                    f"Expected '{expected_type}, got '{actual_type}'",
                )
