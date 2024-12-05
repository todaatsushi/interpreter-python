import abc
import dataclasses as dc
import logging

from interpreter import tokens

logger = logging.getLogger(__name__)


class Node(abc.ABC):
    @abc.abstractmethod
    def token_literal(self) -> str:
        pass

    @abc.abstractmethod
    def __str__(self) -> str:
        pass


class Statement(Node):
    @abc.abstractmethod
    def statement_node(self) -> None:
        pass

    def __str__(self) -> str:
        logger.warning("TODO - str for statement")
        return ""


class Expression(Node):
    @abc.abstractmethod
    def expression_node(self) -> None:
        pass

    def __str__(self) -> str:
        logger.warning("TODO - str for expression")
        return ""


@dc.dataclass
class Program(Node):
    statements: list[Statement] = dc.field(default_factory=list)

    def token_literal(self) -> str:
        if len(self.statements) > 0:
            return self.statements[0].token_literal()
        return ""

    def __str__(self) -> str:
        s = ""
        for statement in self.statements:
            s = f"{s}{str(statement)}\n"
        return s


@dc.dataclass
class Identifier(Expression):
    token: tokens.Token
    value: str

    def expression_node(self) -> None:
        pass

    def token_literal(self) -> str:
        assert self.token.value
        return self.token.value.decode("ascii")

    def __str__(self) -> str:
        return self.value


@dc.dataclass
class IntegerLiteral(Expression):
    token: tokens.Token
    value: str

    def expression_node(self) -> None:
        pass

    def token_literal(self) -> int:
        assert self.token.value
        return int(self.token.value.decode("ascii"))

    def __str__(self) -> str:
        return self.value


@dc.dataclass
class Let(Statement):
    token: tokens.Token
    name: Identifier

    # TODO - needs not nullable expression later
    value: Expression | None = None

    def statement_node(self) -> None:
        pass

    def token_literal(self) -> str:
        assert self.token.value
        return self.token.value.decode("ascii")

    def __str__(self) -> str:
        s = f"{self.token_literal()} {str(self.name)} ="
        if self.value:
            s = f"{s} {str(self.value)}"
        return f"{s};"


@dc.dataclass
class Return(Statement):
    token: tokens.Token

    # TODO - needs not nullable expression later
    value: Expression | None = None

    def statement_node(self) -> None:
        pass

    def token_literal(self) -> str:
        assert self.token.value
        return self.token.value.decode("ascii")

    def __str__(self) -> str:
        s = self.token_literal()
        if self.value:
            s = f"{s} {str(self.value)}"
        return f"{s};"


@dc.dataclass
class ExpressionStatement(Statement):
    token: tokens.Token
    expression: Expression | None

    def statement_node(self) -> None:
        pass

    def token_literal(self) -> str:
        assert self.token.value
        return self.token.value.decode("ascii")

    def __str__(self) -> str:
        if self.expression:
            return str(self.expression)
        return ""


@dc.dataclass
class PrefixExpression(Expression):
    token: tokens.Token
    operator: str
    right: Expression

    def expression_node(self) -> None:
        pass

    def token_literal(self) -> str:
        return f"{self.operator}{self.right}"

    def __str__(self) -> str:
        return f"({self.operator}{str(self.right)})"
