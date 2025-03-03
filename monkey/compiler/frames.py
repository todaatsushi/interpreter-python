import dataclasses as dc
from monkey.compiler import code

from monkey.interpreter import objects


@dc.dataclass
class Frame:
    closure: objects.Closure
    instruction_pointer: int
    base_pointer: int

    @classmethod
    def new(cls, func: objects.Closure, base_pointer: int):
        return cls(func, -1, base_pointer)

    @property
    def instructions(self) -> code.Instructions:
        return self.closure.function.instructions
