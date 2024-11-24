from __future__ import annotations

import dataclasses as dc

from interpreter import tokens


@dc.dataclass(frozen=True)
class Lexer:
    @classmethod
    def new(cls, input: str) -> Lexer:
        raise NotImplementedError

    def next_token(self) -> tokens.Token:
        raise NotImplementedError
