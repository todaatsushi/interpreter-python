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


def test_string_object(tc: unittest.TestCase, expected: str, actual: objects.Object):
    tc.assertIsInstance(actual, objects.String)
    assert isinstance(actual, objects.String)

    tc.assertEqual(expected, actual.value)


def test_null_object(tc: unittest.TestCase, actual: objects.Object) -> None:
    tc.assertIs(actual, vm.NULL)


def test_array_object(
    tc: unittest.TestCase, expected: list[objects.Object], actual: objects.Object
) -> None:
    tc.assertIsInstance(actual, objects.Array)
    assert isinstance(actual, objects.Array)

    tc.assertEqual(len(expected), len(actual.items))

    for i, ex in enumerate(expected):
        test_expected_object(tc, ex, actual.items[i])


def test_expected_object(
    tc: unittest.TestCase, expected: object, actual: objects.Object
) -> None:
    if isinstance(expected, bool):
        return test_boolean_object(tc, expected, actual)
    elif isinstance(expected, int):
        return test_integer_object(tc, expected, actual)
    elif isinstance(expected, str):
        return test_string_object(tc, expected, actual)
    elif isinstance(expected, list):
        return test_array_object(tc, expected, actual)
    elif expected is None:
        return test_null_object(tc, actual)
    else:
        raise NotImplementedError(type(expected))


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

            bc = compiler.bytecode()
            virtual_machine = vm.VM.from_bytecode(bc)
            virtual_machine.run()

            test_expected_object(tc, expected, virtual_machine.last_popped_stack_elem)


class TestVM(unittest.TestCase):
    def test_integers(self) -> None:
        run_vm_tests(
            self,
            (
                ("1", 1),
                ("2", 2),
                ("-5", -5),
                ("-10", -10),
                ("-50 + 100 + -50", 0),
                ("(5 + 10 * 2 + 15 / 3) * 2 + -10", 50),
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
                ("1 < 2", True),
                ("1 > 2", False),
                ("1 < 1", False),
                ("1 > 1", False),
                ("1 == 1", True),
                ("1 != 1", False),
                ("1 == 2", False),
                ("1 != 2", True),
                ("true == true", True),
                ("false == false", True),
                ("true == false", False),
                ("true != false", True),
                ("false != true", True),
                ("(1 < 2) == true", True),
                ("(1 < 2) == false", False),
                ("(1 > 2) == true", False),
                ("(1 > 2) == false", True),
                ("!true", False),
                ("!false", True),
                ("!5", False),
                ("!!true", True),
                ("!!false", False),
                ("!!5", True),
                ("!(if (false) { 5; })", True),
            ),
        )

    def test_conditionals(self) -> None:
        run_vm_tests(
            self,
            (
                ("if (true) { 10 }", 10),
                ("if (true) { 10 } else { 20 }", 10),
                ("if (1) { 10 }", 10),
                ("if (false) { 10 } else { 20 } ", 20),
                ("if (1 < 2) { 10 }", 10),
                ("if (1 < 2) { 10 } else { 20 }", 10),
                ("if (1 > 2) { 10 } else { 20 }", 20),
                ("if (1 > 2) { 10 }", None),
                ("if (false) { 10 }", None),
            ),
        )

    def test_global_let_statements(self) -> None:
        run_vm_tests(
            self,
            (
                ("let one = 1; one", 1),
                ("let one = 1; let two = 2; one + two", 3),
                ("let one= 1; let two = one + one; one + two", 3),
            ),
        )

    def test_string(self) -> None:
        run_vm_tests(
            self,
            (
                ('"monkey"', "monkey"),
                ('"mon" + "key"', "monkey"),
                ('"mon" + "key" + "banana"', "monkeybanana"),
            ),
        )

    def test_array(self) -> None:
        run_vm_tests(
            self,
            (
                ("[]", []),
                ("[1, 2, 3]", [1, 2, 3]),
                ("[1 + 2, 3 * 4, 5 + 6]", [3, 12, 11]),
            ),
        )
