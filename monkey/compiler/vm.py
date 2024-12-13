from __future__ import annotations
from typing import TYPE_CHECKING

import dataclasses as dc

from monkey.interpreter import objects
from monkey.compiler import code, compilers

if TYPE_CHECKING:
    from typing import Final

    from monkey.compiler import compilers


STACK_SIZE: Final = 2048


class VMError(Exception):
    pass


class Unhandled(VMError):
    pass


class StackError(VMError):
    pass


class Missing(StackError):
    pass


class Empty(StackError):
    pass


class Overflow(StackError):
    pass


@dc.dataclass
class VM:
    stack_pointer: int

    constants: list[objects.Object]
    instructions: code.Instructions

    stack: list[objects.Object | None] = dc.field(default_factory=list)

    @classmethod
    def from_bytecode(cls, bytecode: compilers.Bytecode) -> VM:
        return cls(
            constants=bytecode.constants,
            instructions=bytecode.instructions,
            stack_pointer=0,
            stack=[None] * STACK_SIZE,
        )

    def run(self) -> None:
        instruction_pointer = 0
        while instruction_pointer < len(self.instructions):
            op_code = code.OpCodes(bytes([self.instructions[instruction_pointer]]))

            match op_code:
                case code.OpCodes.CONSTANT:
                    left = instruction_pointer + 1
                    right = left + 2
                    const_index = int.from_bytes(self.instructions[left:right])

                    to_add = self.constants[const_index]
                    self.push(to_add)
                    instruction_pointer += 2
                case (
                    code.OpCodes.ADD
                    | code.OpCodes.SUBTRACT
                    | code.OpCodes.MULTIPLY
                    | code.OpCodes.DIVIDE
                ):
                    self.execute_binary_operation(op_code)
                case code.OpCodes.POP:
                    self.pop()
                case code.OpCodes.TRUE | code.OpCodes.FALSE:
                    self.execute_binary_boolean_operation(op_code)
                case _:
                    raise NotImplementedError(op_code)

            instruction_pointer += 1

    @property
    def last_popped_stack_elem(self) -> objects.Object:
        if item := self.stack[self.stack_pointer]:
            return item
        raise Empty

    def push(self, o: objects.Object) -> None:
        if self.stack_pointer >= STACK_SIZE:
            raise Overflow

        self.stack[self.stack_pointer] = o
        self.stack_pointer += 1

    def pop(self) -> objects.Object:
        if self.stack_pointer == -1:
            raise Empty

        o = self.stack[self.stack_pointer - 1]
        assert o

        self.stack_pointer -= 1
        return o

    # Operations
    def execute_binary_operation(self, op: code.OpCodes) -> None:
        right = self.pop()
        left = self.pop()

        if isinstance(left, objects.Integer) and isinstance(right, objects.Integer):
            return self.execute_binary_integer_operation(op, left, right)
        raise NotImplementedError(op, left, right)

    def execute_binary_integer_operation(
        self, op: code.OpCodes, left: objects.Integer, right: objects.Integer
    ) -> None:
        match op:
            case code.OpCodes.ADD:
                result = left.value + right.value
            case code.OpCodes.MULTIPLY:
                result = left.value * right.value
            case code.OpCodes.SUBTRACT:
                result = left.value - right.value
            case code.OpCodes.DIVIDE:
                result = left.value // right.value
            case _:
                raise Unhandled(op)
        self.push(objects.Integer(value=result))

    def execute_binary_boolean_operation(self, op_code: code.OpCodes) -> None:
        assert op_code in [code.OpCodes.TRUE, code.OpCodes.FALSE]
