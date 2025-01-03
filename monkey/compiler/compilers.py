from __future__ import annotations

import dataclasses as dc

from monkey.compiler import code
from monkey.interpreter import ast
from monkey.interpreter import objects


class CompilerError(Exception):
    pass


class CouldntCompile(CompilerError):
    pass


@dc.dataclass
class Bytecode:
    instructions: code.Instructions = dc.field(default_factory=code.Instructions)
    constants: list[objects.Object] = dc.field(default_factory=list)


@dc.dataclass
class Compiler:
    instructions: code.Instructions = dc.field(default_factory=code.Instructions)
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
                    self.emit(code.OpCodes.POP)
                case ast.Infix:
                    assert isinstance(node, ast.Infix) and node.right
                    if node.operator == "<":
                        self.compile(node.right)
                        self.compile(node.left)
                        self.emit(code.OpCodes.GREATER_THAN)
                        return

                    self.compile(node.left)
                    self.compile(node.right)

                    match node.operator:
                        case "+":
                            self.emit(code.OpCodes.ADD)
                        case "-":
                            self.emit(code.OpCodes.SUBTRACT)
                        case "/":
                            self.emit(code.OpCodes.DIVIDE)
                        case "*":
                            self.emit(code.OpCodes.MULTIPLY)
                        case ">":
                            self.emit(code.OpCodes.GREATER_THAN)
                        case "==":
                            self.emit(code.OpCodes.EQUAL)
                        case "!=":
                            self.emit(code.OpCodes.NOT_EQUAL)
                        case _:
                            raise NotImplementedError(node.operator)
                case ast.Prefix:
                    assert isinstance(node, ast.Prefix) and node.right
                    self.compile(node.right)

                    match node.operator:
                        case "!":
                            self.emit(code.OpCodes.EXCLAIMATION_MARK)
                        case "-":
                            self.emit(code.OpCodes.MINUS)
                        case _:
                            raise NotImplementedError
                case ast.IntegerLiteral:
                    assert isinstance(node, ast.IntegerLiteral)
                    integer = objects.Integer(value=node.value)
                    self.emit(code.OpCodes.CONSTANT, self._add_constant(integer))
                case ast.BooleanLiteral:
                    assert isinstance(node, ast.BooleanLiteral)
                    op_code = code.OpCodes.TRUE if node.value else code.OpCodes.FALSE
                    self.emit(op_code)
                case _:
                    raise NotImplementedError
        except Exception as exc:
            raise CouldntCompile(str(exc)) from exc

    def bytecode(self) -> Bytecode:
        return Bytecode(instructions=self.instructions, constants=self.constants)
