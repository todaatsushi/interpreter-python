from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from interpreter import ast, objects


def node(node: ast.Node) -> objects.Object:
    raise NotImplementedError
