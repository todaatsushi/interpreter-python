from __future__ import annotations

import enum
import dataclasses as dc


class TokenType(enum.StrEnum):
    ILLEGAL = "ILLEGAL"
    EOF = "EOF"

    # Identifiers + literals
    IDENTIFIER = "IDENTIFIER"  # add, x, y
    INT = "INT"
    STRING = "STRING"
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
    COLON = ":"

    LEFT_PARENTHESES = "("
    RIGHT_PARENTHESES = ")"
    LEFT_BRACE = "{"
    RIGHT_BRACE = "}"
    LESS_THAN = "<"
    MORE_THAN = ">"
    LEFT_SQUARE_BRACKET = "["
    RIGHT_SQUARE_BRACKET = "]"

    # Other
    EXCLAIMATION_MARK = "!"

    # Evaluators
    EQUALS = "=="
    NOT_EQUALS = "!="

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
    ":": TokenType.COLON,
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
    '"': TokenType.STRING,
    "[": TokenType.LEFT_SQUARE_BRACKET,
    "]": TokenType.RIGHT_SQUARE_BRACKET,
}

COULD_BE_DOUBLE = {TokenType.EXCLAIMATION_MARK, TokenType.ASSIGN}
