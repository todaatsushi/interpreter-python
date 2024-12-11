import unittest

from monkey.compiler import code


class TestOpCodes(unittest.TestCase):
    def test_make(self) -> None:
        test_cases: tuple[tuple[code.OpCodes, list[int], bytes], ...] = (
            (
                code.OpCodes.CONSTANT,
                [65534],
                bytes([code.OpCodes.CONSTANT.as_int(), 255, 254]),
            ),
        )

        for op, operands, expected in test_cases:
            with self.subTest(f"{op}: {operands}"):
                instruction = code.make(op, *operands)
                self.assertEqual(instruction, expected)

    def test_string(self) -> None:
        instructions = [
            code.make(code.OpCodes.CONSTANT, i)
            for i in [
                1,
                2,
                65535,
            ]
        ]

        expected = "0000 OpConstant 1\n0003 OpConstant 2\n0006 OpConstant 65535"

        concatted = code.Instructions.concat_bytes(instructions)
        self.assertEqual(str(concatted), expected)

    def test_read_operands(self) -> None:
        test_cases: tuple[tuple[code.OpCodes, list[int], int], ...] = (
            (code.OpCodes.CONSTANT, [1], 2),
            (code.OpCodes.CONSTANT, [65535], 2),
        )

        for op, operands, bytes_read in test_cases:
            with self.subTest(str(op)):
                instruction = code.make(op, *operands)

                try:
                    definition = code.lookup_byte(code.OpCodes(op))
                except (ValueError, code.NotFound) as exc:
                    self.fail(exc)

                # Without opcode
                operands_read, n = code.read_operands(definition, instruction[1:])
                self.assertEqual(n, bytes_read)
                self.assertEqual(operands_read, operands)
