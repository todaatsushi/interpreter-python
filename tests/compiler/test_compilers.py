import unittest

from monkey import code, compilers
from monkey.interpreter import ast, lexers, objects, parsers


def parse(code: str) -> ast.Program:
    lexer = lexers.Lexer.new(code)
    parser = parsers.Parser.new(lexer)
    program = parser.parse_program()
    if parser.errors:
        raise Exception(["\n".join(e for e in parser.errors)])
    return program


def test_constants(
    tc: unittest.TestCase, expected: list[object], actual: list[objects.Object]
) -> None:
    tc.assertEqual(len(expected), len(actual))

    for i, exp in enumerate(expected):
        if isinstance(exp, int):
            tc.assertIsInstance(actual[i], objects.Integer)
            assert isinstance(actual[i], objects.Integer)

            tc.assertEqual(actual[i].value, exp)
        else:
            tc.fail(f"{type(exp)} not supported")


def test_instructions(
    tc: unittest.TestCase,
    expected: list[code.Instructions],
    actual: code.Instructions,
) -> None:
    all_instructions = [i for i in expected]
    for i, instruction in enumerate(all_instructions):
        tc.assertEqual(
            instruction, actual[i], f"Expected '{instruction}', got '{actual[i]}'"
        )


class TestCompiler(unittest.TestCase):
    def test_integer_arithmetic(self) -> None:
        test_cases: tuple[tuple[str, list[object], list[code.Instructions]], ...] = (
            ("1 + 2", [1, 2], [code.make(code.OpCodes.CONSTANT, i) for i in range(2)]),
        )

        for input_, expected_constants, expected_instructions in test_cases:
            with self.subTest(input_):
                program = parse(input_)
                compiler = compilers.Compiler.new()

                try:
                    compiler.compile(program)
                except Exception as exc:
                    self.fail(str(exc))

                bytecode = compiler.bytecode()

                with self.subTest("Instructions"):
                    test_instructions(
                        self, expected_instructions, bytecode.instructions
                    )

                with self.subTest("Constants"):
                    test_constants(self, expected_constants, bytecode.constants)


class TestInstructions(unittest.TestCase):
    def test_string(self) -> None:
        instructions = [code.make(code.OpCodes.CONSTANT, i) for i in [1, 2, 65535]]

        expected = """
        0000 OpConstant 1
        0003 OpConstant 2
        0006 OpConstant 65535
        """.strip()

        concatted = code.Instructions.concat_bytes(instructions)
        self.assertEqual(str(concatted), expected)

    def test_read_operands(self) -> None:
        test_cases: tuple[tuple[code.OpCodes, list[int], int], ...] = tuple()

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
