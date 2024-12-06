import abc
import enum
import dataclasses as dc


class ObjectType(enum.StrEnum):
    INTEGER = "INTEGER"


class Object(abc.ABC):
    type: ObjectType

    @abc.abstractmethod
    def inspect(self) -> str:
        pass


@dc.dataclass
class Integer(Object):
    value: int

    type = ObjectType.INTEGER

    def inspect(self) -> str:
        return str(self.value)
