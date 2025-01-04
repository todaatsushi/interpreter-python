import unittest

from monkey.compiler import code, compilers
from monkey.interpreter import objects
from tests import utils


def run_compiler_tests(
    tc: unittest.TestCase,
    test_cases: tuple[tuple[str, list[object], list[code.Instructions]], ...],
) -> None:
    for input_, expected_constants, expected_instructions in test_cases:
        with tc.subTest(input_):
            program = utils.parse(input_)
            compiler = compilers.Compiler.new()

            try:
                compiler.compile(program)
            except compilers.CouldntCompile as exc:
                tc.fail(
                    f"Couldn't compile program{': ' + str(exc) if str(exc) else '.'}"
                )

            bytecode = compiler.bytecode()

            with tc.subTest(f"{input_}: instructions"):
                test_instructions(tc, expected_instructions, bytecode.instructions)

            with tc.subTest(f"{input_}: constants"):
                test_constants(tc, expected_constants, bytecode.constants)


def test_constants(
    tc: unittest.TestCase, expected: list[object], actual: list[objects.Object]
) -> None:
    tc.assertEqual(
        len(expected),
        len(actual),
        f"Expected {len(expected)} bytes, got:\n\n{expected}\n\nvs\n\n{actual}",
    )

    for i, exp in enumerate(expected):
        if isinstance(exp, int):
            tc.assertIsInstance(actual[i], objects.Integer)
            assert isinstance(actual[i], objects.Integer)

            tc.assertEqual(actual[i].value, exp)
        elif isinstance(exp, str):
            tc.assertIsInstance(actual[i], objects.String)
            assert isinstance(actual[i], objects.String)

            tc.assertEqual(actual[i].value, exp)
        else:
            tc.fail(f"{type(exp)} not supported")


def test_instructions(
    tc: unittest.TestCase,
    expected: list[code.Instructions],
    actual: code.Instructions,
) -> None:
    all_instructions = code.Instructions.concat_bytes(expected)
    tc.assertEqual(
        len(actual),
        len(all_instructions),
        f"Expected {len(all_instructions)} bytes, expected:\n\n{all_instructions}\n\nvs\n\n{actual}",
    )

    for i, instruction in enumerate(all_instructions):
        tc.assertEqual(
            instruction,
            actual[i],
            f"Expected '{instruction}' at position {i}, got '{actual[i]}'",
        )


class TestCompiler(unittest.TestCase):
    def test_integers_arithmetic(self) -> None:
        run_compiler_tests(
            self,
            (
                (
                    "1 + 2",
                    [1, 2],
                    [
                        *[code.make(code.OpCodes.CONSTANT, i) for i in range(2)],
                        code.make(code.OpCodes.ADD),
                        code.make(code.OpCodes.POP),
                    ],
                ),
                (
                    "1 - 2",
                    [1, 2],
                    [
                        code.make(code.OpCodes.CONSTANT, 0),
                        code.make(code.OpCodes.CONSTANT, 1),
                        code.make(code.OpCodes.SUBTRACT),
                        code.make(code.OpCodes.POP),
                    ],
                ),
                (
                    "1 * 2",
                    [1, 2],
                    [
                        code.make(code.OpCodes.CONSTANT, 0),
                        code.make(code.OpCodes.CONSTANT, 1),
                        code.make(code.OpCodes.MULTIPLY),
                        code.make(code.OpCodes.POP),
                    ],
                ),
                (
                    "1 / 2",
                    [1, 2],
                    [
                        code.make(code.OpCodes.CONSTANT, 0),
                        code.make(code.OpCodes.CONSTANT, 1),
                        code.make(code.OpCodes.DIVIDE),
                        code.make(code.OpCodes.POP),
                    ],
                ),
                (
                    "-1",
                    [1],
                    [
                        code.make(code.OpCodes.CONSTANT, 0),
                        code.make(code.OpCodes.MINUS),
                        code.make(code.OpCodes.POP),
                    ],
                ),
            ),
        )

    def test_expression_pops(self) -> None:
        run_compiler_tests(
            self,
            (
                (
                    ("1; 2"),
                    [1, 2],
                    [
                        code.make(code.OpCodes.CONSTANT, 0),
                        code.make(code.OpCodes.POP),
                        code.make(code.OpCodes.CONSTANT, 1),
                        code.make(code.OpCodes.POP),
                    ],
                ),
            ),
        )

    def test_boolean_expressions(self) -> None:
        run_compiler_tests(
            self,
            (
                (
                    "true",
                    [],
                    [
                        code.make(code.OpCodes.TRUE),
                        code.make(code.OpCodes.POP),
                    ],
                ),
                (
                    "false",
                    [],
                    [
                        code.make(code.OpCodes.FALSE),
                        code.make(code.OpCodes.POP),
                    ],
                ),
                (
                    "1 > 2",
                    [1, 2],
                    [
                        code.make(code.OpCodes.CONSTANT, 0),
                        code.make(code.OpCodes.CONSTANT, 1),
                        code.make(code.OpCodes.GREATER_THAN),
                        code.make(code.OpCodes.POP),
                    ],
                ),
                (
                    "1 < 2",
                    [2, 1],
                    [
                        code.make(code.OpCodes.CONSTANT, 0),
                        code.make(code.OpCodes.CONSTANT, 1),
                        code.make(code.OpCodes.GREATER_THAN),
                        code.make(code.OpCodes.POP),
                    ],
                ),
                (
                    "1 == 2",
                    [1, 2],
                    [
                        code.make(code.OpCodes.CONSTANT, 0),
                        code.make(code.OpCodes.CONSTANT, 1),
                        code.make(code.OpCodes.EQUAL),
                        code.make(code.OpCodes.POP),
                    ],
                ),
                (
                    "1 != 2",
                    [1, 2],
                    [
                        code.make(code.OpCodes.CONSTANT, 0),
                        code.make(code.OpCodes.CONSTANT, 1),
                        code.make(code.OpCodes.NOT_EQUAL),
                        code.make(code.OpCodes.POP),
                    ],
                ),
                (
                    "true == false",
                    [],
                    [
                        code.make(code.OpCodes.TRUE),
                        code.make(code.OpCodes.FALSE),
                        code.make(code.OpCodes.EQUAL),
                        code.make(code.OpCodes.POP),
                    ],
                ),
                (
                    "true != false",
                    [],
                    [
                        code.make(code.OpCodes.TRUE),
                        code.make(code.OpCodes.FALSE),
                        code.make(code.OpCodes.NOT_EQUAL),
                        code.make(code.OpCodes.POP),
                    ],
                ),
                (
                    "!true",
                    [],
                    [
                        code.make(code.OpCodes.TRUE),
                        code.make(code.OpCodes.EXCLAIMATION_MARK),
                        code.make(code.OpCodes.POP),
                    ],
                ),
            ),
        )

    def test_conditionals(self) -> None:
        run_compiler_tests(
            self,
            (
                (
                    "if (true) { 10 }; 3333;",
                    [10, 3333],
                    [
                        code.make(code.OpCodes.TRUE),
                        code.make(code.OpCodes.JUMP_NOT_TRUTHY, 10),
                        code.make(code.OpCodes.CONSTANT, 0),
                        code.make(code.OpCodes.JUMP, 11),
                        code.make(code.OpCodes.NULL),
                        code.make(code.OpCodes.POP),
                        code.make(code.OpCodes.CONSTANT, 1),
                        code.make(code.OpCodes.POP),
                    ],
                ),
                (
                    "if (true) { 10 } else {20}; 3333;",
                    [10, 20, 3333],
                    [
                        code.make(code.OpCodes.TRUE),
                        code.make(code.OpCodes.JUMP_NOT_TRUTHY, 10),
                        code.make(code.OpCodes.CONSTANT, 0),
                        code.make(code.OpCodes.JUMP, 13),
                        code.make(code.OpCodes.CONSTANT, 1),
                        code.make(code.OpCodes.POP),
                        code.make(code.OpCodes.CONSTANT, 2),
                        code.make(code.OpCodes.POP),
                    ],
                ),
            ),
        )

    def test_global_let_statements(self) -> None:
        run_compiler_tests(
            self,
            (
                (
                    ("let one = 1;\nlet two = 2;"),
                    [1, 2],
                    [
                        code.make(code.OpCodes.CONSTANT, 0),
                        code.make(code.OpCodes.SET_GLOBAL, 0),
                        code.make(code.OpCodes.CONSTANT, 1),
                        code.make(code.OpCodes.SET_GLOBAL, 1),
                    ],
                ),
                (
                    "let one = 1;\n one;",
                    [1],
                    [
                        code.make(code.OpCodes.CONSTANT, 0),
                        code.make(code.OpCodes.SET_GLOBAL, 0),
                        code.make(code.OpCodes.GET_GLOBAL, 0),
                        code.make(code.OpCodes.POP),
                    ],
                ),
                (
                    "let one = 1;\nlet two = one;\ntwo;",
                    [1],
                    [
                        code.make(code.OpCodes.CONSTANT, 0),
                        code.make(code.OpCodes.SET_GLOBAL, 0),
                        code.make(code.OpCodes.GET_GLOBAL, 0),
                        code.make(code.OpCodes.SET_GLOBAL, 1),
                        code.make(code.OpCodes.GET_GLOBAL, 1),
                        code.make(code.OpCodes.POP),
                    ],
                ),
            ),
        )

    def test_string(self) -> None:
        run_compiler_tests(
            self,
            (
                (
                    '"monkey"',
                    ["monkey"],
                    [
                        code.make(code.OpCodes.CONSTANT, 0),
                        code.make(code.OpCodes.POP),
                    ],
                ),
                (
                    '"mon" + "key"',
                    ["mon", "key"],
                    [
                        code.make(code.OpCodes.CONSTANT, 0),
                        code.make(code.OpCodes.CONSTANT, 1),
                        code.make(code.OpCodes.ADD),
                        code.make(code.OpCodes.POP),
                    ],
                ),
            ),
        )

    def test_array(self) -> None:
        run_compiler_tests(
            self,
            (
                (
                    "[]",
                    [],
                    [
                        code.make(code.OpCodes.ARRAY, 0),
                        code.make(code.OpCodes.POP),
                    ],
                ),
                (
                    "[1, 2, 3]",
                    [1, 2, 3],
                    [
                        code.make(code.OpCodes.CONSTANT, 0),
                        code.make(code.OpCodes.CONSTANT, 1),
                        code.make(code.OpCodes.CONSTANT, 2),
                        code.make(code.OpCodes.ARRAY, 3),
                        code.make(code.OpCodes.POP),
                    ],
                ),
                (
                    "[1 + 2, 3 - 4, 5 * 6]",
                    [1, 2, 3, 4, 5, 6],
                    [
                        code.make(code.OpCodes.CONSTANT, 0),
                        code.make(code.OpCodes.CONSTANT, 1),
                        code.make(code.OpCodes.ADD),
                        code.make(code.OpCodes.CONSTANT, 2),
                        code.make(code.OpCodes.CONSTANT, 3),
                        code.make(code.OpCodes.SUBTRACT),
                        code.make(code.OpCodes.CONSTANT, 4),
                        code.make(code.OpCodes.CONSTANT, 5),
                        code.make(code.OpCodes.MULTIPLY),
                        code.make(code.OpCodes.ARRAY, 3),
                        code.make(code.OpCodes.POP),
                    ],
                ),
            ),
        )

    def test_hash_map(self) -> None:
        run_compiler_tests(
            self,
            (
                (
                    "{}",
                    [],
                    [
                        code.make(code.OpCodes.HASH, 0),
                        code.make(code.OpCodes.POP),
                    ],
                ),
                (
                    "{1: 2, 3: 4, 5: 6}",
                    [1, 2, 3, 4, 5, 6],
                    [
                        code.make(code.OpCodes.CONSTANT, 0),
                        code.make(code.OpCodes.CONSTANT, 1),
                        code.make(code.OpCodes.CONSTANT, 2),
                        code.make(code.OpCodes.CONSTANT, 3),
                        code.make(code.OpCodes.CONSTANT, 4),
                        code.make(code.OpCodes.CONSTANT, 5),
                        code.make(code.OpCodes.HASH, 6),
                        code.make(code.OpCodes.POP),
                    ],
                ),
                (
                    "{1: 2 + 3, 4: 5 * 6}",
                    [1, 2, 3, 4, 5, 6],
                    [
                        code.make(code.OpCodes.CONSTANT, 0),
                        code.make(code.OpCodes.CONSTANT, 1),
                        code.make(code.OpCodes.CONSTANT, 2),
                        code.make(code.OpCodes.ADD),
                        code.make(code.OpCodes.CONSTANT, 3),
                        code.make(code.OpCodes.CONSTANT, 4),
                        code.make(code.OpCodes.CONSTANT, 5),
                        code.make(code.OpCodes.MULTIPLY),
                        code.make(code.OpCodes.HASH, 4),
                        code.make(code.OpCodes.POP),
                    ],
                ),
            ),
        )
