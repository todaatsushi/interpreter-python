from __future__ import annotations

import dataclasses as dc

from interpreter import tokens as tk


@dc.dataclass
class Lexer:
    input: str
    position: int
    read_position: int
    literal: bytes | None

    @classmethod
    def new(cls, input: str) -> Lexer:
        instance = cls(input=input, position=0, read_position=0, literal=None)
        instance.read_char()
        return instance

    def read_char(self):
        if self.read_position >= len(self.input):
            self.literal = None
        else:
            self.literal = self.input[self.read_position].encode("ascii")
        self.position = self.read_position
        self.read_position += 1

    def get_current(self) -> str | None:
        if self.literal is not None:
            return self.literal.decode("ascii")
        return self.literal

    def next_token(self) -> tk.Token:
        token_type: tk.TokenType
        value = self.get_current()
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
            case "let":
                token_type = tk.TokenType.LET
            case None | "":
                token_type = tk.TokenType.EOF
            case _:
                raise NotImplementedError

        self.read_char()
        return tk.Token(type=token_type, value=value.encode("ascii") if value else None)
