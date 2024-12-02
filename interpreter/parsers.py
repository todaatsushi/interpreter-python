from __future__ import annotations

import logging

import dataclasses as dc

from interpreter import ast, lexers, tokens

logger = logging.getLogger(__name__)


@dc.dataclass
class Parser:
    lexer: lexers.Lexer

    current_token: tokens.Token
    peek_token: tokens.Token

    @classmethod
    def new(cls, lexer: lexers.Lexer) -> Parser:
        current = lexer.next_token()
        peek = lexer.next_token()
        return cls(lexer=lexer, current_token=current, peek_token=peek)

    def next_token(self) -> None:
        self.current_token = self.peek_token
        self.peek_token = self.lexer.next_token()

    def expect_token_type(
        self, token: tokens.Token, token_type: tokens.TokenType
    ) -> bool:
        if token.type == token_type:
            self.next_token()
            return True
        return False

    def parse_program(self) -> ast.Program:
        raise NotImplementedError


def parse_statement(parser: Parser) -> ast.Statement:
    match parser.current_token.type:
        case tokens.TokenType.LET:
            return parse_let_statement(parser)
        case _:
            raise NotImplementedError


def parse_let_statement(parser: Parser) -> ast.Let:
    let_token = parser.current_token
    assert parser.expect_token_type(parser.peek_token, tokens.TokenType.IDENTIFIER)

    assert parser.current_token.value
    name = ast.Identifier(
        token=parser.current_token, value=parser.current_token.value.decode("ascii")
    )
    assert parser.expect_token_type(parser.peek_token, tokens.TokenType.ASSIGN)

    while not parser.expect_token_type(
        parser.current_token, tokens.TokenType.SEMICOLON
    ):
        logger.info("TODO: fetch value expression")
        parser.next_token()

    return ast.Let(token=let_token, name=name)
