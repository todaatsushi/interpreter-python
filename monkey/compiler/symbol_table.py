from __future__ import annotations

import enum
import dataclasses as dc


class Scope(enum.StrEnum):
    GLOBAL = "GLOBAL"


@dc.dataclass(frozen=True)
class Symbol:
    name: str
    scope: Scope
    index: int


@dc.dataclass
class SymbolTable:
    store: dict[str, Symbol]
    num_definitions: int

    @classmethod
    def new(cls) -> SymbolTable:
        return cls({}, 0)

    def define(self, identifier: str) -> Symbol:
        raise NotImplementedError

    def resolve(self, identifier: str) -> Symbol:
        raise NotImplementedError
