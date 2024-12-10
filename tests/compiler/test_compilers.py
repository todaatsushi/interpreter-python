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
    pass


def test_instructions(
    tc: unittest.TestCase,
    expected: list[code.Instructions],
    actual: code.Instructions,
) -> None:
    pass


class TestCompiler(unittest.TestCase):
    def test_integer_arithmetic(self) -> None:
        test_cases: tuple[tuple[str, list[object], list[code.Instructions]], ...] = (
            tuple()
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
