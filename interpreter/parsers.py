from __future__ import annotations

from collections.abc import Callable, Iterator
import enum

import logging

import dataclasses as dc
from typing import Literal, TypeAlias, TypedDict

from interpreter import ast, lexers, tokens

logger = logging.getLogger(__name__)


PrefixParseFunction: TypeAlias = Callable[[], ast.Expression | None]
InfixParseFunction: TypeAlias = Callable[[ast.Expression], ast.Expression | None]


class ParseFunctionMap(TypedDict):
    PREFIX: dict[tokens.TokenType, PrefixParseFunction]
    INFIX: dict[tokens.TokenType, InfixParseFunction]


class Precedences(enum.IntEnum):
    """
    aka. Order of operations.

    Lowest to highest.
    """

    LOWEST = 1
    EQUALS = 2
    LESSGREATER = 3
    SUM = 4
    PRODUCT = 5
    PREFIX = 6
    CALL = 7

    @classmethod
    def from_token_type(cls, token_type: tokens.TokenType) -> Precedences:
        match token_type:
            case tokens.TokenType.EQUALS | tokens.TokenType.NOT_EQUALS:
                return Precedences.EQUALS
            case tokens.TokenType.LESS_THAN | tokens.TokenType.MORE_THAN:
                return Precedences.LESSGREATER
            case tokens.TokenType.PLUS | tokens.TokenType.MINUS:
                return Precedences.SUM
            case tokens.TokenType.DIVIDE | tokens.TokenType.MULTIPLY:
                return Precedences.PRODUCT
            case _:
                return Precedences.LOWEST


@dc.dataclass
class Parser:
    lexer: lexers.Lexer

    current_token: tokens.Token
    peek_token: tokens.Token

    errors: list[str] = dc.field(default_factory=list, init=False)
    parse_functions: ParseFunctionMap = dc.field(init=False)

    def __post_init__(self) -> None:
        prefix_map: dict[tokens.TokenType, PrefixParseFunction] = {}
        infix_map: dict[tokens.TokenType, InfixParseFunction] = {}
        self.parse_functions: ParseFunctionMap = {
            "PREFIX": prefix_map,
            "INFIX": infix_map,
        }

        # Register prefix
        self.register_prefix(tokens.TokenType.IDENTIFIER, func=self.parse_identifer)
        self.register_prefix(tokens.TokenType.INT, func=self.parse_integer_literal)
        self.register_prefix(
            tokens.TokenType.EXCLAIMATION_MARK, func=self.parse_prefix_expression
        )
        self.register_prefix(tokens.TokenType.MINUS, func=self.parse_prefix_expression)

        # Register infix
        for token_type in (
            tokens.TokenType.EQUALS,
            tokens.TokenType.NOT_EQUALS,
            tokens.TokenType.PLUS,
            tokens.TokenType.MINUS,
            tokens.TokenType.LESS_THAN,
            tokens.TokenType.MORE_THAN,
            tokens.TokenType.MULTIPLY,
            tokens.TokenType.DIVIDE,
        ):
            self.register_infix(token_type, func=self.parse_infix_expression)

    @classmethod
    def new(cls, lexer: lexers.Lexer) -> Parser:
        current = lexer.next_token()
        peek = lexer.next_token()
        return cls(lexer=lexer, current_token=current, peek_token=peek)

    def next_token(self) -> None:
        self.current_token = self.peek_token
        self.peek_token = self.lexer.next_token()

    def expect_token_type(
        self, token: tokens.Token, token_type: tokens.TokenType, fwd: bool
    ) -> bool:
        if token.type == token_type:
            if fwd:
                self.next_token()
            return True
        return False

    def register_prefix(
        self,
        token_type: tokens.TokenType,
        *,
        func: PrefixParseFunction,
    ) -> None:
        self.parse_functions["PREFIX"][token_type] = func

    def register_infix(
        self, token_type: tokens.TokenType, *, func: InfixParseFunction
    ) -> None:
        self.parse_functions["INFIX"][token_type] = func

    ## Precendence

    def get_precendence(self, token: Literal["CURRENT", "PEEK"]) -> Precedences:
        token_to_check = self.current_token if token == "CURRENT" else self.peek_token
        return Precedences.from_token_type(token_to_check.type)

    ## Parsing

    def parse_program(self) -> ast.Program:
        program = ast.Program()

        while self.current_token.type != tokens.TokenType.EOF:
            try:
                statement = next(self.parse_statement())
                if statement:
                    program.statements.append(statement)
            except NotImplementedError:
                logger.warning("TODO")
            except StopIteration:
                break
            finally:
                self.next_token()

        if self.errors:
            logger.error(f"Errors when parsing program: \n{'\n'.join(self.errors)}")

        return program

    def parse_statement(self) -> Iterator[ast.Statement | None]:
        match self.current_token.type:
            case tokens.TokenType.LET:
                yield self.parse_let_statement()
            case tokens.TokenType.RETURN:
                yield self.parse_return_statement()
            case _:
                yield self.parse_expression_statement()

    def parse_expression_statement(self) -> ast.ExpressionStatement:
        expression_statement = ast.ExpressionStatement(
            token=self.current_token,
            expression=self.parse_expression(Precedences.LOWEST),
        )

        if self.expect_token_type(self.peek_token, tokens.TokenType.SEMICOLON, False):
            self.next_token()

        return expression_statement

    def parse_let_statement(self) -> ast.Let | None:
        let_token = self.current_token
        if not self.expect_token_type(
            self.peek_token, tokens.TokenType.IDENTIFIER, True
        ):
            msg = f"Expected {tokens.TokenType.IDENTIFIER}, got {self.peek_token.type} at position {self.lexer.position}."
            self.errors.append(msg)
            return None

        assert self.current_token.value
        name = ast.Identifier(
            token=self.current_token, value=self.current_token.value.decode("ascii")
        )
        if not self.expect_token_type(self.peek_token, tokens.TokenType.ASSIGN, True):
            msg = f"Expected {tokens.TokenType.ASSIGN}, got {self.peek_token.type} at position {self.lexer.position}."
            self.errors.append(msg)
            return None

        while not self.expect_token_type(
            self.current_token, tokens.TokenType.SEMICOLON, False
        ):
            logger.info("TODO: fetch value expression")
            self.next_token()

        return ast.Let(token=let_token, name=name)

    def parse_return_statement(self) -> ast.Return:
        return_token = self.current_token

        self.next_token()

        while not self.expect_token_type(
            self.current_token, tokens.TokenType.SEMICOLON, False
        ):
            logger.info("TODO: fetch value expression")
            self.next_token()

        return ast.Return(token=return_token)

    def parse_identifer(self) -> ast.Identifier:
        assert self.current_token.value
        return ast.Identifier(
            token=self.current_token,
            value=self.current_token.value.decode("ascii"),
        )

    def parse_integer_literal(self) -> ast.IntegerLiteral | None:
        assert self.current_token.value
        value = self.current_token.value.decode("ascii")

        try:
            value = int(value)
        except ValueError:
            msg = f"Couldn't parse '{value}' as int at line {self.lexer.position}."
            self.errors.append(msg)
            return None

        return ast.IntegerLiteral(token=self.current_token, value=str(value))

    def parse_prefix_expression(self) -> ast.Prefix:
        assert self.current_token.value
        token = self.current_token
        operator = self.current_token.value.decode("ascii")

        self.next_token()

        return ast.Prefix(
            token=token,
            operator=operator,
            right=self.parse_expression(Precedences.PREFIX),
        )

    def parse_infix_expression(self, left: ast.Expression) -> ast.Infix:
        current = self.current_token
        assert current.value

        precendence = self.get_precendence("CURRENT")
        self.next_token()

        right = self.parse_expression(precendence)
        return ast.Infix(
            token=current,
            operator=current.value.decode("ascii"),
            left=left,
            right=right,
        )

    def parse_expression(self, precendence: Precedences) -> ast.Expression | None:
        prefix_func = self.parse_functions["PREFIX"].get(self.current_token.type)
        if prefix_func is None:
            msg = f"No prefix parse function for {self.current_token.type} found."
            self.errors.append(msg)
            return None

        left = prefix_func()
        while not self.expect_token_type(
            self.peek_token, tokens.TokenType.SEMICOLON, False
        ) and precendence < self.get_precendence("PEEK"):
            infix_func = self.parse_functions["INFIX"].get(self.peek_token.type)
            if infix_func is None:
                return left

            self.next_token()

            assert left
            left = infix_func(left)
        return left
