from __future__ import annotations

import enum
import dataclasses as dc


class SymbolError(Exception):
    pass


class MissingDefinition(SymbolError):
    pass


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
        symbol = Symbol(identifier, Scope.GLOBAL, self.num_definitions)

        self.store[identifier] = symbol
        self.num_definitions += 1

        return symbol

    def resolve(self, identifier: str) -> Symbol:
        try:
            return self.store[identifier]
        except KeyError as exc:
            raise MissingDefinition(identifier) from exc
