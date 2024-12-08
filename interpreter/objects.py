from __future__ import annotations

import abc
from collections.abc import Mapping
import enum
import dataclasses as dc

from interpreter import ast, environment


class ObjectType(enum.StrEnum):
    NULL = "NULL"
    INTEGER = "INTEGER"
    BOOLEAN = "BOOLEAN"
    RETURN = "RETURN"
    ERROR = "ERROR"
    BUILTIN_FUNCTION = "BUILTIN_FUNCTION"
    FUNCTION = "FUNCTION"
    STRING = "STRING"
    ARRAY = "ARRAY"
    HASH_KEY = "HASH_KEY"
    HASH = "HASH"


class ErrorTypes(enum.StrEnum):
    TYPE_MISMATCH = "type mismatch"
    UNKNOWN_OPERATOR = "unknown operator"
    MISSING_IDENTIFER = "missing identifier"
    NOT_A_FUNC = "not a function"
    INVALID_INDEX = "invalid index"
    KEY_ERROR = "key error"


class Object(abc.ABC):
    type: ObjectType
    value: object

    @abc.abstractmethod
    def inspect(self) -> str:
        pass


@dc.dataclass(frozen=True)
class HashKey:
    type = ObjectType.HASH_KEY

    value: int


class Hashable(Object):
    @abc.abstractmethod
    def hash_key(self) -> HashKey:
        pass


@dc.dataclass(frozen=True)
class Integer(Hashable):
    value: int

    type = ObjectType.INTEGER

    def hash_key(self) -> HashKey:
        return HashKey(value=self.value)

    def inspect(self) -> str:
        return str(self.value)


@dc.dataclass(frozen=True)
class Boolean(Hashable):
    value: bool

    type = ObjectType.BOOLEAN

    def hash_key(self) -> HashKey:
        return HashKey(value=self.value)

    def inspect(self) -> str:
        return str(self.value).lower()


TRUE = Boolean(True)
FALSE = Boolean(False)


@dc.dataclass(frozen=True)
class String(Hashable):
    value: str

    type = ObjectType.STRING

    def hash_key(self) -> HashKey:
        return HashKey(value=int.from_bytes(self.value.encode("utf-8")))

    def inspect(self) -> str:
        return self.value


@dc.dataclass(frozen=True)
class Null(Object):
    value: None = None
    type = ObjectType.NULL

    def inspect(self) -> str:
        return "null"


NULL = Null()


@dc.dataclass(frozen=True)
class Array(Object):
    items: list[Object]

    type = ObjectType.ARRAY

    def inspect(self) -> str:
        return f"[{', '.join(str(item) for item in self.items)}]"


@dc.dataclass(frozen=True)
class HashPair(Object):
    key: Object
    value: Object

    def inspect(self) -> str:
        return f"{str(self.key)} : {str(self.value)}"


@dc.dataclass(frozen=True)
class Hash(Object):
    pairs: Mapping[HashKey, HashPair]

    type = ObjectType.HASH

    def inspect(self) -> str:
        s = "{"
        for _, v in self.pairs.items():
            s = str(v.inspect())
        s = s + "}"
        return s


@dc.dataclass(frozen=True)
class Return(Object):
    value: Object

    type = ObjectType.RETURN

    def inspect(self) -> str:
        return self.value.inspect()


@dc.dataclass(frozen=True)
class Error(Object):
    message: str

    type = ObjectType.ERROR

    def inspect(self) -> str:
        return f"ERROR: {self.message}"


@dc.dataclass(frozen=True)
class Function(Object):
    body: ast.BlockStatement
    env: environment.Environment
    parameters: list[ast.Identifier] = dc.field(default_factory=list)

    type = ObjectType.FUNCTION

    def inspect(self) -> str:
        params = [str(param) for param in self.parameters]
        s = f"fn({', '.join(params)})" + "{\n"
        return f"{s}{str(self.body)}" + "\n}"


class F(abc.ABC):
    """
    aka Built in function - avoid name overlap with evaluated object.
    """

    @abc.abstractmethod
    def __call__(self, *args: Object, **kwargs: Object) -> Object:
        raise NotImplementedError


class GetLength(F):
    WRONG_NUM_ARGS = "wrong number of arguments, got {}, want 1"
    UNSUPPORTED_TYPE = "argument to 'len' not supported, got"

    def __call__(self, *args: Object, **kwargs: Object) -> Object:
        if len(args) != 1 or len(kwargs) != 0:
            return Error(message=self.WRONG_NUM_ARGS.format(len(args) + len(kwargs)))

        arg = args[0]
        if isinstance(arg, String):
            return Integer(value=len(arg.value))

        return Error(message=f"{self.UNSUPPORTED_TYPE} {arg.type}")

    def __str__(self) -> str:
        return "len"


class First(F):
    WRONG_NUM_ARGS = "wrong number of arguments, got {}, want 1"
    NO_KWARGS = "kwargs not supported"
    UNSUPPORTED_TYPE = "argument to 'first' not supported, got"

    def __call__(self, *args: Object, **kwargs: Object) -> Object:
        if len(kwargs):
            return Error(message=self.NO_KWARGS)

        if len(args) != 1:
            return Error(message=self.WRONG_NUM_ARGS.format(len(args)))

        arg = args[0]
        if isinstance(arg, Array):
            if not arg.items:
                return NULL
            return arg.items[0]
        return Error(message=f"{self.UNSUPPORTED_TYPE} {arg.type}")


class Last(F):
    WRONG_NUM_ARGS = "wrong number of arguments, got {}, want 1"
    NO_KWARGS = "kwargs not supported"
    UNSUPPORTED_TYPE = "argument to 'last' not supported, got"

    def __call__(self, *args: Object, **kwargs: Object) -> Object:
        if len(kwargs):
            return Error(message=self.NO_KWARGS)

        if len(args) != 1:
            return Error(message=self.WRONG_NUM_ARGS.format(len(args)))

        arg = args[0]
        if isinstance(arg, Array):
            if not arg.items:
                return NULL
            return arg.items[-1]
        return Error(message=f"{self.UNSUPPORTED_TYPE} {arg.type}")


class Rest(F):
    WRONG_NUM_ARGS = "wrong number of arguments, got {}, want 1"
    NO_KWARGS = "kwargs not supported"
    UNSUPPORTED_TYPE = "argument to 'rest' not supported, got"

    def __call__(self, *args: Object, **kwargs: Object) -> Object:
        if len(kwargs):
            return Error(message=self.NO_KWARGS)

        if len(args) != 1:
            return Error(message=self.WRONG_NUM_ARGS.format(len(args)))

        arg = args[0]
        if isinstance(arg, Array):
            if not arg.items:
                return Array(items=[])
            return Array(items=[item for item in arg.items[1:]])
        return Error(message=f"{self.UNSUPPORTED_TYPE} {arg.type}")


class Push(F):
    NO_KWARGS = "kwargs not supported"
    WRONG_NUM_ARGS = "wrong number of arguments, got {}, want 2"
    UNSUPPORTED_TYPE = "argument to 'rest' at position 1 not supported, got"

    def __call__(self, *args: Object, **kwargs: Object) -> Object:
        if len(kwargs):
            return Error(message=self.NO_KWARGS)

        if len(args) != 2:
            return Error(message=self.WRONG_NUM_ARGS.format(len(args)))

        arg = args[0]
        if isinstance(arg, Array):
            return Array(items=[item for item in arg.items] + [args[1]])
        return Error(message=f"{self.UNSUPPORTED_TYPE} {arg.type}")


@dc.dataclass(frozen=True)
class BuiltInFunction(Object):
    function: F

    type = ObjectType.BUILTIN_FUNCTION

    def inspect(self) -> str:
        return str(self.function)


BUILTIN_MAP: dict[str, BuiltInFunction] = {
    "len": BuiltInFunction(function=GetLength()),
    "first": BuiltInFunction(function=First()),
    "last": BuiltInFunction(function=Last()),
    "rest": BuiltInFunction(function=Rest()),
    "push": BuiltInFunction(function=Push()),
}
