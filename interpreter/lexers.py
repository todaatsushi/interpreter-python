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

    def skip_whitespace(self) -> None:
        is_whitespace = lambda c: c is not None and not c.strip()
        while is_whitespace(self.get_current()):
            self.read_char()

    def _read_multi(self) -> str:
        """
        For multi character tokens (e.g. identifiers), stream until ending character given.

        At this point, the current char is asserted to be a number or letter.
        """
        value = self.get_current()
        should = lambda c: c and c.isalnum()
        while should(value):
            self.read_char()
            _next = self.get_current()
            if not should(_next):
                break

            assert _next and value
            value += _next
        assert value
        return value

    def next_token(self) -> tk.Token:
        token_type: tk.TokenType

        self.skip_whitespace()

        multi = False  # any calls to _read_multi have already gone to the next char
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
                if value.isalnum():
                    value = self._read_multi()
                    if value.isalpha():
                        token_type = tk.TOKEN_TYPE_MAP.get(value, tk.TokenType.IDENTIFIER)
                    else:
                        token_type = tk.TokenType.INT
                    multi = True
                else:
                    token_type = tk.TokenType.ILLEGAL
        if not multi:
            self.read_char()
        return tk.Token(type=token_type, value=value.encode("ascii") if value else None)
