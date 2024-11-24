from __future__ import annotations

import enum
import dataclasses as dc

class TokenType(enum.StrEnum):
    ILLEGAL = "ILLEGAL"
    EOF = "EOF"

    # Identifiers + literals
    IDENT = "IDENT" # add, x, y
    INT = "INT"

    # Operators
    ASSIGN = "="
    PLUS = "+"

    # Delimiters
    COMMA = ","
    SEMICOLON = ";"

    LEFT_PARENTHESES = "("
    RIGHT_PARENTHESES = ")"
    LEFT_BRACE = "{"
    RIGHT_BRACE = "}"

    # Keywords
    FUNCTION = "FUNCTION"
    LET = "LET"


@dc.dataclass(frozen=True)
class Token:
    type: TokenType
    value: str
