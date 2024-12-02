from __future__ import annotations


import dataclasses as dc

from interpreter import lexers, tokens


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
