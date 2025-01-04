from __future__ import annotations
from typing import TYPE_CHECKING

import dataclasses as dc

from monkey.interpreter import objects
from monkey.compiler import code, compilers

if TYPE_CHECKING:
    from typing import Final

    from monkey.compiler import compilers


STACK_SIZE: Final = 2048
GLOBALS_SIZE: Final = 65536

TRUE = objects.Boolean(value=True)
FALSE = objects.Boolean(value=False)
NULL = objects.Null()


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


def is_truthy(obj: objects.Object) -> bool:
    if isinstance(obj, objects.Boolean):
        return obj.value
    return True


@dc.dataclass
class VM:
    stack_pointer: int
    stack: list[objects.Object | None]

    globals: list[objects.Object | None]

    constants: list[objects.Object]
    instructions: code.Instructions

    @classmethod
    def from_bytecode(
        cls,
        bytecode: compilers.Bytecode,
        state: list[objects.Object | None] | None = None,
    ) -> VM:
        return cls(
            globals=state or ([None] * GLOBALS_SIZE),
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
                    const_index = code.read_int16(
                        self.instructions, instruction_pointer + 1
                    )

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
                    self.push(TRUE if op_code == code.OpCodes.TRUE else FALSE)
                case (
                    code.OpCodes.GREATER_THAN
                    | code.OpCodes.EQUAL
                    | code.OpCodes.NOT_EQUAL
                ):
                    self.execute_comparison(op_code)
                case code.OpCodes.MINUS | code.OpCodes.EXCLAIMATION_MARK:
                    self.execute_operator(op_code)
                case code.OpCodes.JUMP:
                    position = code.read_int16(
                        self.instructions, instruction_pointer + 1
                    )
                    instruction_pointer = position - 1
                case code.OpCodes.JUMP_NOT_TRUTHY:
                    position = code.read_int16(
                        self.instructions, instruction_pointer + 1
                    )
                    instruction_pointer += 2

                    cond = self.pop()
                    if not is_truthy(cond):
                        instruction_pointer = position - 1
                case code.OpCodes.NULL:
                    self.push(NULL)
                case code.OpCodes.SET_GLOBAL:
                    global_index = code.read_int16(
                        self.instructions, instruction_pointer + 1
                    )
                    instruction_pointer += 2
                    self.globals[global_index] = self.pop()
                case code.OpCodes.GET_GLOBAL:
                    global_index = code.read_int16(
                        self.instructions, instruction_pointer + 1
                    )
                    instruction_pointer += 2

                    obj = self.globals[global_index]
                    assert obj
                    self.push(obj)
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
        if self.stack_pointer <= 0:
            raise Empty

        o = self.stack[self.stack_pointer - 1]
        if o is None:
            raise Missing(f"No value at {self.stack_pointer - 1}")

        self.stack_pointer -= 1
        return o

    # Operations
    def execute_binary_operation(self, op: code.OpCodes) -> None:
        right = self.pop()
        left = self.pop()

        if isinstance(left, objects.Integer) and isinstance(right, objects.Integer):
            return self.execute_binary_integer_operation(op, left, right)
        elif isinstance(left, objects.String) and isinstance(right, objects.String):
            return self.execute_binary_string_operation(op, left, right)
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

    def execute_operator(self, op: code.OpCodes) -> None:
        match op:
            case code.OpCodes.MINUS:
                return self.execute_minus_operator()
            case code.OpCodes.EXCLAIMATION_MARK:
                return self.execute_exclaimation_mark_operator()
            case _:
                raise Unhandled(f"Not a valid prefix operator: {str(op)}")

    def execute_exclaimation_mark_operator(self) -> None:
        operand = self.pop()

        if operand is TRUE:
            self.push(FALSE)
        elif operand is FALSE:
            self.push(TRUE)
        elif operand is NULL:
            self.push(TRUE)
        else:
            self.push(FALSE)

    def execute_minus_operator(self) -> None:
        operand = self.pop()

        if not isinstance(operand, objects.Integer):
            raise Unhandled(operand)

        self.push(objects.Integer(value=operand.value * -1))

    def execute_comparison(self, op: code.OpCodes) -> None:
        right = self.pop()
        left = self.pop()

        if isinstance(left, objects.Integer) and isinstance(right, objects.Integer):
            return self.execute_integer_comparison(op, left, right)
        if isinstance(left, objects.Boolean) and isinstance(right, objects.Boolean):
            return self.execute_boolean_comparison(op, left, right)

        raise Unhandled(f"{op} between {type(left)} and {type(right)}")

    def execute_integer_comparison(
        self, op: code.OpCodes, left: objects.Integer, right: objects.Integer
    ) -> None:
        result: bool
        match op:
            case code.OpCodes.EQUAL:
                result = left.value == right.value
            case code.OpCodes.GREATER_THAN:
                result = left.value > right.value
            case code.OpCodes.NOT_EQUAL:
                result = left.value != right.value
            case _:
                raise Unhandled(f"{op} not handled for integer comparisons.")
        self.push(objects.Boolean(value=result))

    def execute_binary_string_operation(
        self, op: code.OpCodes, left: objects.String, right: objects.String
    ) -> None:
        result: str

        match op:
            case code.OpCodes.ADD:
                result = left.value + right.value
            case _:
                raise Unhandled(op)

        self.push(objects.String(value=result))

    def execute_boolean_comparison(
        self, op: code.OpCodes, left: objects.Boolean, right: objects.Boolean
    ) -> None:
        result: bool
        left = TRUE if left.value else FALSE
        right = TRUE if right.value else FALSE

        match op:
            case code.OpCodes.EQUAL:
                result = left is right
            case code.OpCodes.NOT_EQUAL:
                result = left is not right
            case _:
                raise Unhandled(f"{op} not handled for boolean comparisons.")
        self.push(TRUE if result else FALSE)
