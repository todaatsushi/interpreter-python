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
        return cls(input=input, position=0, read_position=0, char=None)

    def next_token(self) -> tokens.Token:
        raise NotImplementedError
