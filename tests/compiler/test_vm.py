import unittest
from monkey.compiler import compilers, vm

from monkey.interpreter import objects
from tests import utils


def test_integer_object(
    tc: unittest.TestCase, expected: int, actual: objects.Object
) -> None:
    tc.assertIsInstance(actual, objects.Integer)
    assert isinstance(actual, objects.Integer)

    tc.assertEqual(expected, actual.value)


def test_boolean_object(
    tc: unittest.TestCase, expected: bool, actual: objects.Object
) -> None:
    tc.assertIsInstance(actual, objects.Boolean)
    assert isinstance(actual, objects.Boolean)

    tc.assertEqual(expected, actual.value)


def test_expected_object(
    tc: unittest.TestCase, expected: object, actual: objects.Object
) -> None:
    with tc.subTest("Testing expected object"):
        if isinstance(expected, bool):
            return test_boolean_object(tc, expected, actual)
        if isinstance(expected, int):
            return test_integer_object(tc, expected, actual)


def run_vm_tests(
    tc: unittest.TestCase, test_cases: tuple[tuple[str, object], ...]
) -> None:
    for input_, expected in test_cases:
        compiler = compilers.Compiler.new()
        program = utils.parse(input_)

        with tc.subTest(input_):
            try:
                compiler.compile(program)
            except compilers.CouldntCompile as exc:
                tc.fail(str(exc))

            virtual_machine = vm.VM.from_bytecode(compiler.bytecode())
            virtual_machine.run()

            test_expected_object(tc, expected, virtual_machine.last_popped_stack_elem)


class TestArithmetic(unittest.TestCase):
    def test_integers(self) -> None:
        run_vm_tests(
            self,
            (
                ("1", 1),
                ("2", 2),
            ),
        )

    def test_integer_operations(self) -> None:
        run_vm_tests(
            self,
            (
                ("1 - 2", -1),
                ("1 * 2", 2),
                ("1 + 2", 3),
                ("4 / 2", 2),
                ("50 / 2 * 2 + 10 - 5", 55),
                ("5 + 5 + 5 + 5 - 10", 10),
                ("2 * 2 * 2 * 2 * 2", 32),
                ("5 * 2 + 10", 20),
                ("5 + 2 * 10", 25),
                ("5 * (2 + 10)", 60),
            ),
        )

    def test_booleans(self) -> None:
        run_vm_tests(
            self,
            (
                ("true", True),
                ("false", False),
            ),
        )
