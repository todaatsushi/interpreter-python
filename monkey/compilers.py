from __future__ import annotations

import dataclasses as dc
from typing import TYPE_CHECKING

from monkey import code

if TYPE_CHECKING:
    from monkey.interpreter import objects, ast


class CompilerError(Exception):
    pass


class CouldntCompile(CompilerError):
    pass


@dc.dataclass
class Bytecode:
    instructions: code.Instructions = dc.field(init=False, default_factory=bytes)
    constants: list[objects.Object] = dc.field(init=False, default_factory=list)


@dc.dataclass
class Compiler:
    instructions: code.Instructions = dc.field(init=False, default_factory=bytes)
    constants: list[objects.Object] = dc.field(init=False, default_factory=list)

    @classmethod
    def new(cls) -> Compiler:
        return cls()

    def compile(self, program: ast.Program) -> None:
        try:
            raise NotImplementedError
        except Exception as exc:
            raise CouldntCompile from exc

    def bytecode(self) -> Bytecode:
        return Bytecode()
