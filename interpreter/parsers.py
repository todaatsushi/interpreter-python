from __future__ import annotations


import dataclasses as dc

from interpreter import ast, lexers, tokens


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

    def parse_program(self) -> ast.Program:
        raise NotImplementedError
