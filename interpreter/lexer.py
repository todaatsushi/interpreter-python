from __future__ import annotations

import dataclasses as dc


@dc.dataclass(frozen=True)
class Lexer:
    @classmethod
    def new(cls) -> Lexer:
        raise NotImplementedError

    def next_token(self) -> str:
        raise NotImplementedError
