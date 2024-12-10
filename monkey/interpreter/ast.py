import abc
from collections.abc import Mapping
import dataclasses as dc
import logging

from monkey.interpreter import tokens

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


@dc.dataclass(frozen=True)
class Program(Node):
    statements: list[Statement] = dc.field(default_factory=list)

    def token_literal(self) -> str:
        if len(self.statements) > 0:
            return self.statements[0].token_literal()
        return ""

    def __str__(self) -> str:
        s = ""
        for statement in self.statements:
            s = f"{s}{str(statement)}"
        return s


@dc.dataclass(frozen=True)
class BlockStatement(Node):
    token: tokens.Token  # ie. {
    statements: list[Statement] = dc.field(default_factory=list)

    def statement_node(self) -> None:
        pass

    def token_literal(self) -> str:
        assert self.token.value
        return self.token.value.decode("ascii")

    def __str__(self) -> str:
        s = ""
        for statement in self.statements:
            s = f"{s}{str(statement)}"
        return s


@dc.dataclass(frozen=True)
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


@dc.dataclass(frozen=True)
class IntegerLiteral(Expression):
    token: tokens.Token
    value: int

    def expression_node(self) -> None:
        pass

    def token_literal(self) -> str:
        assert self.token.value
        return self.token.value.decode("ascii")

    def __str__(self) -> str:
        return str(self.value)


@dc.dataclass(frozen=True)
class ArrayLiteral(Expression):
    token: tokens.Token  # ie. [
    items: list[Expression]

    def expression_node(self) -> None:
        pass

    def token_literal(self) -> str:
        assert self.token.value
        return self.token.value.decode("ascii")

    def __str__(self) -> str:
        return f"[{', '.join(str(i) for i in self.items)}]"


@dc.dataclass(frozen=True)
class BooleanLiteral(Expression):
    token: tokens.Token
    value: bool

    def expression_node(self) -> None:
        pass

    def token_literal(self) -> str:
        return str(self.value).lower()

    def __str__(self) -> str:
        return self.token_literal()


@dc.dataclass(frozen=True)
class FunctionLiteral(Expression):
    token: tokens.Token  # ie. fn
    parameters: list[Identifier]
    body: BlockStatement | None

    def expression_node(self) -> None:
        pass

    def token_literal(self) -> str:
        assert self.token.value
        return self.token.value.decode("ascii")

    def __str__(self) -> str:
        params = ",".join(str(param) for param in self.parameters)
        return f"{str(self.token.value)} ({params}) {str(self.body)}"


@dc.dataclass(frozen=True)
class StringLiteral(Expression):
    token: tokens.Token  # ie. "
    value: str

    def expression_node(self) -> None:
        pass

    def token_literal(self) -> str:
        assert self.token.value
        return self.token.value.decode("ascii")

    def __str__(self) -> str:
        return self.value


@dc.dataclass(frozen=True)
class Let(Statement):
    token: tokens.Token
    name: Identifier

    value: Expression

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


@dc.dataclass(frozen=True)
class Return(Statement):
    token: tokens.Token

    value: Expression

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


@dc.dataclass(frozen=True)
class ExpressionStatement(Statement):
    token: tokens.Token
    expression: Expression

    def statement_node(self) -> None:
        pass

    def token_literal(self) -> str:
        assert self.token.value
        return self.token.value.decode("ascii")

    def __str__(self) -> str:
        if self.expression:
            return str(self.expression)
        return ""


@dc.dataclass(frozen=True)
class Prefix(Expression):
    token: tokens.Token
    operator: str
    right: Expression | None

    def expression_node(self) -> None:
        pass

    def token_literal(self) -> str:
        return f"{self.operator}{self.right}"

    def __str__(self) -> str:
        return f"({self.operator}{str(self.right)})"


@dc.dataclass(frozen=True)
class Infix(Expression):
    token: tokens.Token  # ie. the operator

    left: Expression
    operator: str
    right: Expression | None

    def expression_node(self) -> None:
        pass

    def token_literal(self) -> str:
        assert self.token.value
        return self.token.value.decode("ascii")

    def __str__(self) -> str:
        return f"({self.left} {self.operator} {self.right})"


@dc.dataclass(frozen=True)
class Index(Expression):
    token: tokens.Token  # ie. [
    left: Expression
    index: Expression

    def expression_node(self) -> None:
        pass

    def token_literal(self) -> str:
        assert self.token.value
        return self.token.value.decode("ascii")

    def __str__(self) -> str:
        return f"({str(self.left)}[{str(self.index)}])"


@dc.dataclass(frozen=True)
class Map(Expression):
    token: tokens.Token  # ie. {

    pairs: Mapping[Expression, Expression]

    def expression_node(self) -> None:
        pass

    def token_literal(self) -> str:
        assert self.token.value
        return self.token.value.decode("ascii")

    def __str__(self) -> str:
        s = "{"
        for k, v in self.pairs.items():
            s = f"{k} : {str(v)}"
        s = s + "}"
        return s


@dc.dataclass(frozen=True)
class If(Expression):
    token: tokens.Token  # ie. if

    condition: Expression

    consequence: BlockStatement | None
    alternative: BlockStatement | None

    def expression_node(self) -> None:
        pass

    def token_literal(self) -> str:
        assert self.token.value
        return self.token.value.decode("ascii")

    def __str__(self) -> str:
        s = f"if {str(self.condition)}"
        if self.consequence:
            s = f"{s} {self.consequence}"
        if self.alternative:
            s = f"{s} else {self.alternative}"
        return s


@dc.dataclass(frozen=True)
class Call(Expression):
    token: tokens.Token  # ie. (

    function: Identifier | FunctionLiteral
    arguments: list[Expression]

    def expression_node(self) -> None:
        pass

    def token_literal(self) -> str:
        assert self.token.value
        return self.token.value.decode("ascii")

    def __str__(self) -> str:
        args = [str(arg) for arg in self.arguments]
        return f"{str(self.function)}({', '.join(args)})"
