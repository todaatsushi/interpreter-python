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

            virtual_machine = vm.VM.new()
            virtual_machine.run()

            test_expected_object(tc, expected, virtual_machine.stack_top())
