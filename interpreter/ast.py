import abc


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
