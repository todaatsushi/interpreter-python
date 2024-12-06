import abc
import enum


class ObjectType(enum.StrEnum):
    pass


class Object(abc.ABC):
    type: ObjectType

    @abc.abstractmethod
    def inspect(self) -> str:
        pass
