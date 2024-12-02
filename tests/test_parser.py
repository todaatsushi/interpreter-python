import unittest

from interpreter import lexers, parsers, tokens


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
