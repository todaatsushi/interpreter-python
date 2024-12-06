from __future__ import annotations

import abc
import enum
import dataclasses as dc


class ObjectType(enum.StrEnum):
    NULL = "NULL"
    INTEGER = "INTEGER"
    BOOLEAN = "BOOLEAN"
    RETURN = "RETURN"
    ERROR = "ERROR"


class Object(abc.ABC):
    type: ObjectType
    value: object

    @abc.abstractmethod
    def inspect(self) -> str:
        pass


@dc.dataclass
class Integer(Object):
    value: int

    type = ObjectType.INTEGER

    def inspect(self) -> str:
        return str(self.value)


@dc.dataclass
class Boolean(Object):
    value: bool

    type = ObjectType.BOOLEAN

    def inspect(self) -> str:
        return str(self.value).lower()


TRUE = Boolean(True)
FALSE = Boolean(False)


@dc.dataclass
class Null(Object):
    value: None = None
    type = ObjectType.NULL

    def inspect(self) -> str:
        return "null"


NULL = Null()


@dc.dataclass
class Return(Object):
    value: Object

    type = ObjectType.RETURN

    def inspect(self) -> str:
        return self.value.inspect()


@dc.dataclass
class Error(Object):
    message: str

    type = ObjectType.ERROR

    def inspect(self) -> str:
        return f"ERROR: {self.message}"
