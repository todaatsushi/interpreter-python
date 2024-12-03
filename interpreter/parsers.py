from __future__ import annotations

import logging

import dataclasses as dc

from interpreter import ast, lexers, tokens

logger = logging.getLogger(__name__)


class ParseError(Exception):
    pass


@dc.dataclass
class Parser:
    lexer: lexers.Lexer

    current_token: tokens.Token
    peek_token: tokens.Token

    errors: list[str] = dc.field(default_factory=list)

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

    ## Parsing

    def parse_program(self) -> ast.Program:
        program = ast.Program()

        while self.current_token.type != tokens.TokenType.EOF:
            try:
                statement = self.parse_statement()
                program.statements.append(statement)
            except NotImplementedError:
                logger.warning("TODO")
                self.next_token()
            except ParseError:
                self.next_token()

        if self.errors:
            logger.error(f"Errors when parsing program: \n{'\n'.join(self.errors)}")

        return program

    def parse_statement(self) -> ast.Statement:
        match self.current_token.type:
            case tokens.TokenType.LET:
                return self.parse_let_statement()
            case tokens.TokenType.RETURN:
                return self.parse_return_statement()
            case _:
                raise NotImplementedError

    def parse_let_statement(self) -> ast.Let:
        let_token = self.current_token
        if not self.expect_token_type(self.peek_token, tokens.TokenType.IDENTIFIER):
            msg = f"Expected {tokens.TokenType.IDENTIFIER}, got {self.peek_token.type} at position {self.lexer.position}."
            self.errors.append(msg)
            raise ParseError(msg)

        assert self.current_token.value
        name = ast.Identifier(
            token=self.current_token, value=self.current_token.value.decode("ascii")
        )
        if not self.expect_token_type(self.peek_token, tokens.TokenType.ASSIGN):
            msg = f"Expected {tokens.TokenType.ASSIGN}, got {self.peek_token.type} at position {self.lexer.position}."
            self.errors.append(msg)
            raise ParseError(msg)

        while not self.expect_token_type(
            self.current_token, tokens.TokenType.SEMICOLON
        ):
            logger.info("TODO: fetch value expression")
            self.next_token()

        return ast.Let(token=let_token, name=name)

    def parse_return_statement(self) -> ast.Return:
        return_token = self.current_token

        self.next_token()

        while not self.expect_token_type(
            self.current_token, tokens.TokenType.SEMICOLON
        ):
            logger.info("TODO: fetch value expression")
            self.next_token()

        return ast.Return(token=return_token)
