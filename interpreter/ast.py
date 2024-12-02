import abc
from collections.abc import Sequence


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


class Program(Node):
    statements: Sequence[Statement]

    def token_literal(self) -> str:
        if len(self.statements) > 0:
            return self.statements[0].token_literal()
        return ""
