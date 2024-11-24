from __future__ import annotations

import enum
import dataclasses as dc

class TokenType(enum.StrEnum):
    pass


@dc.dataclass(frozen=True)
class Token:
    type: TokenType
    value: str
