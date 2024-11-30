from __future__ import annotations

import enum
import dataclasses as dc


class TokenType(enum.StrEnum):
    ILLEGAL = "ILLEGAL"
    EOF = "EOF"

    # Identifiers + literals
    IDENTIFIER = "IDENTIFIER"  # add, x, y
    INT = "INT"

    # Operators
    ASSIGN = "="
    PLUS = "+"
    MULTIPLY = "*"
    DIVIDE = "/"
    MINUS = "-"

    # Delimiters
    COMMA = ","
    SEMICOLON = ";"

    LEFT_PARENTHESES = "("
    RIGHT_PARENTHESES = ")"
    LEFT_BRACE = "{"
    RIGHT_BRACE = "}"
    LESS_THAN = "<"
    MORE_THAN = ">"

    # Other
    EXCLAIMATION_MARK = "!"

    # Keywords
    FUNCTION = "FUNCTION"
    LET = "LET"


@dc.dataclass(frozen=True)
class Token:
    type: TokenType
    value: bytes | None


# Distnguish between identifiers and keywords
TOKEN_TYPE_MAP = {"let": TokenType.LET, "fn": TokenType.FUNCTION}
