from __future__ import annotations

import enum
import dataclasses as dc


class SymbolError(Exception):
    pass


class MissingDefinition(SymbolError):
    pass


class Scope(enum.StrEnum):
    GLOBAL = "GLOBAL"
    LOCAL = "LOCAL"
    BUILTIN = "BUILTIN"
    FREE = "FREE"


@dc.dataclass(frozen=True)
class Symbol:
    name: str
    scope: Scope
    index: int


@dc.dataclass
class SymbolTable:
    store: dict[str, Symbol]
    num_definitions: int

    outer: SymbolTable | None = None

    @classmethod
    def new(cls) -> SymbolTable:
        return cls({}, 0)

    @classmethod
    def new_enclosed(cls, outer: SymbolTable) -> SymbolTable:
        return cls({}, 0, outer=outer)

    def define(self, identifier: str) -> Symbol:
        symbol = Symbol(
            identifier,
            Scope.GLOBAL if self.outer is None else Scope.LOCAL,
            self.num_definitions,
        )

        self.store[identifier] = symbol
        self.num_definitions += 1

        return symbol

    def define_builtin(self, index: int, name: str) -> Symbol:
        symbol = Symbol(name, Scope.BUILTIN, index)
        self.store[name] = symbol
        return symbol

    def resolve(self, identifier: str) -> Symbol:
        try:
            return self.store[identifier]
        except KeyError as exc:
            if self.outer is None:
                raise MissingDefinition(identifier) from exc
            return self.outer.resolve(identifier)
