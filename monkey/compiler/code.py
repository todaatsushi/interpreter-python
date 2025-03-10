from __future__ import annotations

from collections.abc import Sequence
import dataclasses as dc
import enum
import struct
import logging

logger = logging.getLogger(__name__)


class Instructions(bytearray):
    @classmethod
    def concat_bytes(cls, instructions: Sequence[Instructions]) -> Instructions:
        return cls(b"".join(instructions))

    def _format_instruction(self, definition: Definition, operands: list[int]) -> str:
        num_operands = len(definition.operand_widths)
        if num_operands != len(operands):
            return f"ERROR: operand len {len(operands)} does not match definition {num_operands}"

        match num_operands:
            case 0:
                return f"{definition.name}"
            case 1:
                return f"{definition.name} {operands[0]}"
            case 2:
                return f"{definition.name} {operands[0]} {operands[1]}"
        return f"ERROR: unhandled num_operands for {definition.name}"

    def __str__(self) -> str:
        string = ""
        index = 0
        while index < len(self):
            try:
                definition = lookup_byte(bytes([self[index]]))
            except NotFound:
                logger.exception(str(self[index]))
                continue

            operands, read = read_operands(definition, self[index + 1 :])
            op_code = "{:04}".format(index)
            string = (
                f"{string}\n{op_code} {self._format_instruction(definition, operands)}"
            )
            index += 1 + read
        return string.strip()


class OpCodeException(Exception):
    pass


class NotFound(OpCodeException):
    pass


class OpCodes(bytes, enum.Enum):
    CONSTANT = bytes([0])
    POP = bytes([2])

    ADD = bytes([1])
    SUBTRACT = bytes([3])
    MULTIPLY = bytes([4])
    DIVIDE = bytes([5])

    TRUE = bytes([6])
    FALSE = bytes([7])

    EQUAL = bytes([8])
    NOT_EQUAL = bytes([9])
    GREATER_THAN = bytes([10])

    MINUS = bytes([11])
    EXCLAIMATION_MARK = bytes([12])

    JUMP_NOT_TRUTHY = bytes([13])
    JUMP = bytes([14])

    NULL = bytes([15])

    SET_GLOBAL = bytes([16])
    GET_GLOBAL = bytes([17])

    ARRAY = bytes([18])
    HASH = bytes([19])

    INDEX = bytes([20])

    CALL = bytes([21])

    RETURN = bytes([22])
    RETURN_VALUE = bytes([23])

    GET_LOCAL = bytes([24])
    SET_LOCAL = bytes([25])

    GET_BUILTIN = bytes([26])

    CLOSURE = bytes([27])
    GET_FREE = bytes([28])

    def as_int(self) -> int:
        return int.from_bytes(self)


@dc.dataclass(frozen=True, kw_only=True)
class Definition:
    name: str
    operand_widths: list[int]


DEFINITIONS: dict[OpCodes, Definition] = {
    OpCodes.CONSTANT: Definition(name="OpConstant", operand_widths=[2]),
    OpCodes.ADD: Definition(name="OpAdd", operand_widths=[]),
    OpCodes.POP: Definition(name="OpPop", operand_widths=[]),
    OpCodes.SUBTRACT: Definition(name="OpSub", operand_widths=[]),
    OpCodes.MULTIPLY: Definition(name="OpMul", operand_widths=[]),
    OpCodes.DIVIDE: Definition(name="OpDiv", operand_widths=[]),
    OpCodes.TRUE: Definition(name="OpTrue", operand_widths=[]),
    OpCodes.FALSE: Definition(name="OpFalse", operand_widths=[]),
    OpCodes.EQUAL: Definition(name="OpEqual", operand_widths=[]),
    OpCodes.NOT_EQUAL: Definition(name="OpNotEqual", operand_widths=[]),
    OpCodes.GREATER_THAN: Definition(name="OpGreaterThan", operand_widths=[]),
    OpCodes.MINUS: Definition(name="OpMinus", operand_widths=[]),
    OpCodes.EXCLAIMATION_MARK: Definition(name="OpExclaimationMark", operand_widths=[]),
    OpCodes.JUMP_NOT_TRUTHY: Definition(name="OpJumpNotTruthy", operand_widths=[2]),
    OpCodes.JUMP: Definition(name="OpJump", operand_widths=[2]),
    OpCodes.NULL: Definition(name="OpNull", operand_widths=[]),
    OpCodes.SET_GLOBAL: Definition(name="OpSetGlobal", operand_widths=[2]),
    OpCodes.GET_GLOBAL: Definition(name="OpGetGlobal", operand_widths=[2]),
    OpCodes.ARRAY: Definition(name="OpArray", operand_widths=[2]),
    OpCodes.HASH: Definition(name="OpHash", operand_widths=[2]),
    OpCodes.INDEX: Definition(name="OpIndex", operand_widths=[]),
    OpCodes.CALL: Definition(name="OpCall", operand_widths=[1]),
    OpCodes.RETURN: Definition(name="OpReturn", operand_widths=[]),  # Return null
    OpCodes.RETURN_VALUE: Definition(
        name="OpReturnValue", operand_widths=[]
    ),  # Return stack
    OpCodes.GET_LOCAL: Definition(name="OpGetLocal", operand_widths=[1]),
    OpCodes.SET_LOCAL: Definition(name="OpSetLocal", operand_widths=[1]),
    OpCodes.GET_BUILTIN: Definition(name="OpGetBuiltin", operand_widths=[1]),
    OpCodes.CLOSURE: Definition(name="OpClosure", operand_widths=[2, 1]),
    OpCodes.GET_FREE: Definition(name="OpGetFree", operand_widths=[1]),
}


def lookup_byte(op: bytes) -> Definition:
    try:
        code = OpCodes(op)
        return DEFINITIONS[code]
    except (KeyError, ValueError) as exc:
        raise NotFound(int.from_bytes(op)) from exc


def make(op: OpCodes, *operands: int) -> Instructions:
    """
    Reverse of read_operands.
    """
    try:
        definition = lookup_byte(op)
    except OpCodeException:
        return Instructions()

    instruction_len = sum(definition.operand_widths) + 1
    result = Instructions(instruction_len)
    result[0] = op.as_int()

    offset = 1
    for i, operand in enumerate(operands):
        width = definition.operand_widths[i]
        match width:
            case 0:
                pass
            case 2:
                struct.pack_into(">H", result, offset, operand)
            case 1:
                result[offset] = operand
            case _:
                raise NotImplementedError(width)
        offset += width
    return result


def read_operands(
    definition: Definition, instructions: bytearray
) -> tuple[list[int], int]:
    """
    Reverse of make.
    """
    operands: list[int] = [0] * len(definition.operand_widths)
    offset = 0

    for i, width in enumerate(definition.operand_widths):
        match width:
            case 2:
                operands[i] = read_int16(instructions, offset)
            case 1:
                operands[i] = read_int8(instructions, offset)
            case _:
                raise NotImplementedError(width)
        offset += width
    return operands, offset


def read_int16(bytes_: bytearray, left: int) -> int:
    right = left + 2
    return int.from_bytes(bytes_[left:right])


def read_int8(bytes_: bytearray, left: int) -> int:
    right = left + 1
    return int.from_bytes(bytes_[left:right])
