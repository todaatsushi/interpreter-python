from __future__ import annotations
from typing import TYPE_CHECKING

import dataclasses as dc

from monkey.compiler import code, compilers

if TYPE_CHECKING:
    from typing import Final

    from monkey.interpreter import objects
    from monkey.compiler import compilers


STACK_SIZE: Final = 2048


class VMError(Exception):
    pass


class EmptyStack(VMError):
    pass


@dc.dataclass
class VM:
    stack_pointer: int

    constants: list[objects.Object]
    instructions: code.Instructions

    stack: list[objects.Object] = dc.field(default_factory=list)

    @classmethod
    def from_bytecode(cls, bytecode: compilers.Bytecode) -> VM:
        return cls(
            constants=bytecode.constants,
            instructions=bytecode.instructions,
            stack_pointer=0,
        )

    def run(self) -> None:
        raise NotImplementedError

    @property
    def stack_top(self) -> objects.Object:
        if self.stack_pointer == 0:
            raise EmptyStack
        return self.stack[self.stack_pointer - 1]
