from __future__ import annotations

import dataclasses as dc

from interpreter import tokens


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

    def next_token(self) -> tokens.Token:
        raise NotImplementedError
