from __future__ import annotations

import dataclasses as dc

from monkey.compiler import code, symbol_table as st
from monkey.interpreter import ast
from monkey.interpreter import objects


FAKE_JUMP_VALUE = 9999


class CompilerError(Exception):
    pass


class CouldntCompile(CompilerError):
    pass


@dc.dataclass(kw_only=True, frozen=True)
class EmittedInstruction:
    op_code: code.OpCodes
    position: int


@dc.dataclass
class Bytecode:
    instructions: code.Instructions = dc.field(default_factory=code.Instructions)
    constants: list[objects.Object] = dc.field(default_factory=list)


@dc.dataclass
class Compiler:
    symbol_table: st.SymbolTable

    instructions: code.Instructions = dc.field(default_factory=code.Instructions)
    constants: list[objects.Object] = dc.field(init=False, default_factory=list)

    last_instruction: EmittedInstruction | None = None
    previous_instruction: EmittedInstruction | None = None

    @classmethod
    def new(cls, symbol_table: st.SymbolTable | None = None) -> Compiler:
        return cls(symbol_table or st.SymbolTable.new())

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

    def _set_last_instruction(self, op_code: code.OpCodes, position: int) -> None:
        previous = self.last_instruction
        last = EmittedInstruction(op_code=op_code, position=position)

        self.previous_instruction = previous
        self.last_instruction = last

    def _replace_instruction(
        self, position: int, new_instruction: code.Instructions
    ) -> None:
        self.instructions[position : position + len(new_instruction)] = new_instruction

    def _change_operand(self, position: int, operand: int) -> None:
        op_code = self.instructions[position]
        op = code.OpCodes(bytes([op_code]))
        new_instruction = code.make(op, operand)
        self._replace_instruction(position, new_instruction)

    def _change_jump_location_after_consequence(self, position: int) -> None:
        after_consequence_position = len(self.instructions)
        self._change_operand(position, after_consequence_position)

    def _last_instruction_is_pop(self) -> bool:
        return bool(
            self.last_instruction and self.last_instruction.op_code == code.OpCodes.POP
        )

    def _remove_pop(self) -> None:
        assert self.last_instruction
        self.instructions = code.Instructions(
            self.instructions[: self.last_instruction.position]
        )
        self.last_instruction = self.previous_instruction

    def emit(self, op_code: code.OpCodes, *operands: int) -> int:
        instruction = code.make(op_code, *operands)
        postion = self._add_instruction(instruction)

        self._set_last_instruction(op_code, postion)
        return postion

    def compile(self, node: ast.Node) -> None:
        try:
            match type(node):
                case ast.Program | ast.BlockStatement:
                    assert isinstance(node, ast.Program) or isinstance(
                        node, ast.BlockStatement
                    )
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
                case ast.If:
                    assert isinstance(node, ast.If)
                    self.compile(node.condition)

                    jump_position_non_truthy = self.emit(
                        code.OpCodes.JUMP_NOT_TRUTHY, FAKE_JUMP_VALUE
                    )

                    assert node.consequence
                    self.compile(node.consequence)

                    if self._last_instruction_is_pop():
                        self._remove_pop()

                    jump_position = self.emit(code.OpCodes.JUMP, FAKE_JUMP_VALUE)
                    self._change_jump_location_after_consequence(
                        jump_position_non_truthy
                    )

                    if node.alternative is None:
                        self.emit(code.OpCodes.NULL)
                    else:
                        self.compile(node.alternative)

                        if self._last_instruction_is_pop():
                            self._remove_pop()

                    self._change_jump_location_after_consequence(jump_position)
                case ast.Let:
                    assert isinstance(node, ast.Let)
                    self.compile(node.value)
                    symbol = self.symbol_table.define(node.name.value)
                    self.emit(code.OpCodes.SET_GLOBAL, symbol.index)
                case ast.Identifier:
                    assert isinstance(node, ast.Identifier)
                    try:
                        symbol = self.symbol_table.resolve(node.value)
                        self.emit(code.OpCodes.GET_GLOBAL, symbol.index)
                    except st.MissingDefinition:
                        # TODO - handle this
                        raise
                case ast.StringLiteral:
                    assert isinstance(node, ast.StringLiteral)
                    string = objects.String(value=node.value)
                    self.emit(code.OpCodes.CONSTANT, self._add_constant(string))
                case ast.ArrayLiteral:
                    assert isinstance(node, ast.ArrayLiteral)

                    for item in node.items:
                        self.compile(item)
                    self.emit(code.OpCodes.ARRAY, len(node.items))
                case ast.Map:
                    assert isinstance(node, ast.Map)

                    # Can this be multiple types?
                    keys = sorted(list(node.pairs.keys()), key=lambda x: x.value)  # type: ignore
                    for key in keys:
                        value = node.pairs[key]
                        self.compile(key)
                        self.compile(value)
                    self.emit(code.OpCodes.HASH, len(keys) * 2)
                case _:
                    raise NotImplementedError(type(node))
        except Exception as exc:
            raise CouldntCompile(str(exc)) from exc

    def bytecode(self) -> Bytecode:
        return Bytecode(instructions=self.instructions, constants=self.constants)
