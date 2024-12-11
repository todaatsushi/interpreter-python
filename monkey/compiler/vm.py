from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from monkey.interpreter import objects


class VM:
    @classmethod
    def new(cls) -> VM:
        raise NotImplementedError

    def run(self) -> None:
        raise NotImplementedError

    def stack_top(self) -> objects.Object:
        raise NotImplementedError
