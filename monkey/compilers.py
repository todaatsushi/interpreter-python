from __future__ import annotations

import dataclasses as dc
from typing import TYPE_CHECKING

from monkey import code
from monkey.interpreter import ast

if TYPE_CHECKING:
    from monkey.interpreter import objects


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

    def compile(self, node: ast.Node) -> None:
        try:
            match type(node):
                case ast.Program:
                    assert isinstance(node, ast.Program)
                    for statement in node.statements:
                        self.compile(statement)
                case ast.ExpressionStatement:
                    assert isinstance(node, ast.ExpressionStatement)
                    self.compile(node.expression)
                case ast.Infix:
                    assert isinstance(node, ast.Infix) and node.right
                    self.compile(node.left)
                    self.compile(node.right)
                case _:
                    raise NotImplementedError
        except Exception as exc:
            raise CouldntCompile from exc

    def bytecode(self) -> Bytecode:
        return Bytecode()
