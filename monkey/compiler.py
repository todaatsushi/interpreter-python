from __future__ import annotations

import dataclasses as dc
from typing import TYPE_CHECKING

from monkey import code

if TYPE_CHECKING:
    from monkey.interpreter import objects


@dc.dataclass
class Compiler:
    instructions: code.Instructions = dc.field(init=False, default_factory=bytes)
    constants: list[objects.Object] = dc.field(init=False, default_factory=list)

    @classmethod
    def new(cls) -> Compiler:
        return cls()

    def compile(self) -> None:
        raise NotImplementedError
