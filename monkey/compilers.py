from __future__ import annotations

import dataclasses as dc

from monkey import code
from monkey.interpreter import ast
from monkey.interpreter import objects


class CompilerError(Exception):
    pass


class CouldntCompile(CompilerError):
    pass


@dc.dataclass
class Bytecode:
    instructions: code.Instructions = dc.field(default_factory=bytes)
    constants: list[objects.Object] = dc.field(default_factory=list)


@dc.dataclass
class Compiler:
    instructions: code.Instructions = dc.field(init=False, default_factory=bytes)
    constants: list[objects.Object] = dc.field(init=False, default_factory=list)

    @classmethod
    def new(cls) -> Compiler:
        return cls()

    def _add_constant(self, o: objects.Object) -> int:
        """Returns position"""
        self.constants.append(o)
        return len(self.constants) - 1

    def _add_instruction(self, instruction: code.Instructions) -> int:
        """Returns position"""
        num_instructions = len(self.instructions)
        self.instructions = code.Instructions.concat_bytes(
            [self.instructions, instruction]
        )
        return num_instructions

    def emit(self, op_code: code.OpCodes, *operands: int) -> int:
        instruction = code.make(op_code, *operands)
        return self._add_instruction(instruction)

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
            raise CouldntCompile(str(exc)) from exc

    def bytecode(self) -> Bytecode:
        return Bytecode(instructions=self.instructions, constants=self.constants)
