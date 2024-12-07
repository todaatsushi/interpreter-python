from __future__ import annotations

import dataclasses as dc

from interpreter import tokens as tk


class Unexpected(Exception):
    pass


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

    def read_char(self) -> None:
        if self.read_position >= len(self.input):
            self.literal = None
        else:
            self.literal = self.input[self.read_position].encode("ascii")
        self.position = self.read_position
        self.read_position += 1

    def peek_char(self) -> str | None:
        if self.read_position >= len(self.input):
            return None
        return self.input[self.read_position]

    def get_current(self) -> str | None:
        if self.literal is not None:
            return self.literal.decode("ascii")
        return self.literal

    def skip_whitespace(self) -> None:
        def _is_whitespace(c: str | None) -> bool:
            return c is not None and not c.strip()

        while _is_whitespace(self.get_current()):
            self.read_char()

    def _read_multi(self) -> str:
        """
        For multi character tokens (e.g. identifiers), stream until ending character given.

        At this point, the current char is asserted to be a number or letter.
        """

        def should(c: str | None) -> bool:
            return bool(c) and c.isalnum()

        value = self.get_current()
        while should(value):
            self.read_char()
            _next = self.get_current()
            if not should(_next):
                break

            assert _next and value
            value += _next
        assert value
        return value

    def _match_token_type(
        self, value: str, variable: bool
    ) -> tuple[tk.TokenType, str | None]:
        """
        variable: ie. non single id char token (e.g. =). Could be int, identifier etc.
        """
        if variable:
            token_type = None
            if value.isalnum():
                value = self._read_multi()
                if value.isalpha():
                    token_type = tk.TOKEN_TYPE_MAP.get(value, tk.TokenType.IDENTIFIER)
                else:
                    token_type = tk.TokenType.INT
            else:
                self.read_char()
                token_type = tk.TokenType.ILLEGAL
            return token_type, value
        else:
            if value in (None, ""):
                return tk.TokenType.EOF, value
            if token_type := tk.TOKEN_TYPE_MAP.get(value):
                if token_type == tk.TokenType.STRING:
                    value = ""
                    while self.peek_char() != '"':
                        self.read_char()
                        _current = self.get_current()
                        if _current is None:
                            raise Unexpected("Didn't expect None.")
                        value = f"{value}{_current}"

                    # Skip last str char and second "
                    self.read_char()
                    self.read_char()
                    return token_type, value
                elif token_type not in (
                    tk.TokenType.ASSIGN,
                    tk.TokenType.EXCLAIMATION_MARK,
                ):
                    self.read_char()
                    return token_type, value
                else:
                    next_char = self.peek_char()
                    if value == "=" and next_char == "=":
                        token_type = tk.TokenType.EQUALS
                    elif value == "!" and next_char == "=":
                        token_type = tk.TokenType.NOT_EQUALS
                    else:
                        self.read_char()
                        return token_type, value

                    self.read_char()
                    self.read_char()
                    assert value and next_char
                    return token_type, value + next_char
            return self._match_token_type(value, True)

    def next_token(self) -> tk.Token:
        self.skip_whitespace()

        value = self.get_current()
        if value in (None, ""):
            return tk.Token(type=tk.TokenType.EOF, value=None)

        token_type, value = self._match_token_type(value, False)
        return tk.Token(type=token_type, value=value.encode("ascii") if value else None)
