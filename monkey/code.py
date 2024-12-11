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
            case 1:
                return f"{str(definition.name)} {operands[0]}"
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
    CONSTANT = enum.auto()

    def as_int(self) -> int:
        return int.from_bytes(self)


@dc.dataclass(frozen=True, kw_only=True)
class Definition:
    name: str
    operand_widths: list[int]


DEFINITIONS: dict[OpCodes, Definition] = {
    OpCodes.CONSTANT: Definition(name="OpConstant", operand_widths=[2])
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
            case 2:
                struct.pack_into(">H", result, offset, operand)
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
                operands[i] = int.from_bytes(instructions[offset : offset + width])
            case _:
                raise NotImplementedError(width)
        offset += width
    return operands, offset
