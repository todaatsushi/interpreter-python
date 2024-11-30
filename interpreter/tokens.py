from __future__ import annotations

import enum
import dataclasses as dc


class TokenType(enum.StrEnum):
    ILLEGAL = "ILLEGAL"
    EOF = "EOF"

    # Identifiers + literals
    IDENTIFIER = "IDENTIFIER"  # add, x, y
    INT = "INT"
    TRUE = "TRUE"
    FALSE = "FALSE"

    # Control flow
    IF = "IF"
    ELSE = "ELSE"
    RETURN = "RETURN"

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
TOKEN_TYPE_MAP = {
    "let": TokenType.LET,
    "fn": TokenType.FUNCTION,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "return": TokenType.RETURN,
    # chars
    "+": TokenType.PLUS,
    "=": TokenType.ASSIGN,
    ";": TokenType.SEMICOLON,
    "(": TokenType.LEFT_PARENTHESES,
    ")": TokenType.RIGHT_PARENTHESES,
    "{": TokenType.LEFT_BRACE,
    "}": TokenType.RIGHT_BRACE,
    ",": TokenType.COMMA,
    "-": TokenType.MINUS,
    "/": TokenType.DIVIDE,
    "*": TokenType.MULTIPLY,
    "<": TokenType.LESS_THAN,
    ">": TokenType.MORE_THAN,
    "!": TokenType.EXCLAIMATION_MARK,
}
