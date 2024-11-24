from __future__ import annotations

import dataclasses as dc

from interpreter import tokens as tk


@dc.dataclass
class Lexer:
    input: str
    position: int
    read_position: int
    char: bytes | None

    @classmethod
    def new(cls, input: str) -> Lexer:
        instance = cls(input=input, position=0, read_position=0, char=None)
        instance.read_char()
        return instance

    def read_char(self):
        if self.read_position >= len(self.input):
            self.char = None
        else:
            self.char = self.input[self.read_position].encode("ascii")
        self.position = self.read_position
        self.read_position += 1

    def get_current(self) -> str | None:
        return self.char.decode("ascii").strip() if self.char else None

    def read_token(self) -> str | None:
        """
        Read in input until we hit a readable string of characters
        """
        total = ""
        value = self.get_current()
        while value and value.isalnum():
            self.read_char()
            total += value
            value = self.get_current()

        # Value must be a terminiating character if entered the loop.
        # If not looped, it's the first non alphanumeric char, and return'
        # and validate that it's not whitespace.'
        if value and (v := value.strip()):
            return v
        return total or None

    def next_token(self) -> tk.Token:
        token_type: tk.TokenType
        value = self.read_token()
        match value:
            case "+":
                token_type = tk.TokenType.PLUS
            case "=":
                token_type = tk.TokenType.ASSIGN
            case ";":
                token_type = tk.TokenType.SEMICOLON
            case "(":
                token_type = tk.TokenType.LEFT_PARENTHESES
            case ")":
                token_type = tk.TokenType.RIGHT_PARENTHESES
            case "{":
                token_type = tk.TokenType.LEFT_BRACE
            case "}":
                token_type = tk.TokenType.RIGHT_BRACE
            case ",":
                token_type = tk.TokenType.COMMA
            case None:
                token_type = tk.TokenType.EOF
            case _:
                token_type = tk.TokenType.ILLEGAL

        token = tk.Token(type=token_type, value=self.char)
        self.read_char()
        return token
