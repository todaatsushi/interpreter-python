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

    def read_token(self) -> str | None:
        """
        Read in input until we hit a readable string of characters
        """
        value = self.char.decode("ascii") if self.char else None
        parsed = ""
        while value and value.isalpha():
            parsed += value
            self.read_char()
            value = self.char.decode("ascii") if self.char else None

        if parsed:
            return parsed
        return value

    def next_token(self) -> tk.Token:
        token_type: tk.TokenType
        value = self.char.decode("ascii") if self.char else None
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
