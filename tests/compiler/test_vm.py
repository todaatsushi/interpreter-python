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


def test_expected_object(
    tc: unittest.TestCase, expected: object, actual: objects.Object
) -> None:
    with tc.subTest("Testing expected object"):
        if isinstance(expected, int):
            return test_integer_object(tc, expected, actual)


def run_vm_test(
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
    def test_integer(self) -> None:
        run_vm_test(
            self,
            (
                ("1", 1),
                ("2", 2),
                ("1 + 2", 3),
            ),
        )
