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
    all_instructions = code.Instructions.concat_bytes(expected)
    for i, instruction in enumerate(all_instructions):
        tc.assertEqual(
            instruction,
            actual[i],
            f"Expected '{instruction}' at position {i}, got '{actual[i]}'",
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
                except compilers.CouldntCompile as exc:
                    self.fail(
                        f"Couldn't compile program{': ' + str(exc) if str(exc) else '.'}"
                    )

                bytecode = compiler.bytecode()

                with self.subTest("Instructions"):
                    test_instructions(
                        self, expected_instructions, bytecode.instructions
                    )

                with self.subTest("Constants"):
                    test_constants(self, expected_constants, bytecode.constants)
