import abc
import dataclasses as dc
from collections.abc import Sequence

from interpreter import tokens


class Node(abc.ABC):
    @abc.abstractmethod
    def token_literal(self) -> str:
        pass


class Statement(Node):
    @abc.abstractmethod
    def statement_node(self) -> None:
        pass


class Expression(Node):
    @abc.abstractmethod
    def expression_node(self) -> None:
        pass


@dc.dataclass
class Program(Node):
    statements: Sequence[Statement]

    def token_literal(self) -> str:
        if len(self.statements) > 0:
            return self.statements[0].token_literal()
        return ""


@dc.dataclass
class Identifier(Expression):
    token: tokens.Token
    value: str

    def expression_node(self) -> None:
        pass

    def token_literal(self) -> str:
        assert self.token.value
        return self.token.value.decode("ascii")


@dc.dataclass
class Let(Statement):
    token: tokens.Token
    name: Identifier
    value: Expression

    def statement_node(self) -> None:
        pass

    def token_literal(self) -> str:
        assert self.token.value
        return self.token.value.decode("ascii")
