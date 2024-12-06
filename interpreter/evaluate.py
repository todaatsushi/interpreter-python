from __future__ import annotations
import logging

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from interpreter import ast, objects


logger = logging.getLogger(__name__)


def node(node: ast.Node) -> objects.Object:
    match type(node):
        case _:
            logger.error(f"Unhandled type: {type(node)}")
            raise NotImplementedError
