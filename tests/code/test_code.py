import unittest

from monkey import code


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
