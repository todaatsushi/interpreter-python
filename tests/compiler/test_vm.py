from collections.abc import Mapping, Sequence
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
    tc.assertEqual(actual, vm.NULL)


def test_hash_map_object(
    tc: unittest.TestCase,
    expected: Mapping[objects.HashKey, objects.HashPair],
    actual: objects.Object,
) -> None:
    tc.assertIsInstance(actual, objects.Hash)
    assert isinstance(actual, objects.Hash)

    tc.assertEqual(len(actual.pairs), len(expected))

    for k, v in expected.items():
        tc.assertIn(k, actual.pairs)

        pair = actual.pairs[k]
        test_expected_object(tc, v, pair.value)


def test_array_object(
    tc: unittest.TestCase, expected: list[objects.Object], actual: objects.Object
) -> None:
    tc.assertIsInstance(actual, objects.Array)
    assert isinstance(actual, objects.Array)

    tc.assertEqual(len(expected), len(actual.items))

    for i, ex in enumerate(expected):
        test_expected_object(tc, ex, actual.items[i])


def test_error_object(
    tc: unittest.TestCase, expected: objects.Error, actual: objects.Object
) -> None:
    tc.assertIsInstance(actual, objects.Error)
    assert isinstance(actual, objects.Error)

    tc.assertEqual(expected.message, actual.message)


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
    elif isinstance(expected, Mapping):
        return test_hash_map_object(tc, expected, actual)
    elif expected is None:
        return test_null_object(tc, actual)
    elif isinstance(expected, objects.Error):
        return test_error_object(tc, expected, actual)
    else:
        raise NotImplementedError(type(expected))


def run_vm_tests(
    tc: unittest.TestCase, test_cases: Sequence[tuple[str, object]]
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

    def test_hash(self) -> None:
        run_vm_tests(
            self,
            (
                ("{}", {}),
                (
                    "{1: 2, 2: 3}",
                    {
                        objects.Integer(value=1).hash_key(): 2,
                        objects.Integer(value=2).hash_key(): 3,
                    },
                ),
                (
                    "{1 + 1: 2 * 2, 3 + 3: 4 * 4}",
                    {
                        objects.Integer(value=2).hash_key(): 4,
                        objects.Integer(value=6).hash_key(): 16,
                    },
                ),
            ),
        )

    def test_index_expressions(self) -> None:
        run_vm_tests(
            self,
            (
                ("[1, 2, 3][1]", 2),
                ("[1, 2, 3][0 + 2]", 3),
                ("[[1, 2, 3]][0][0]", 1),
                ("{1: 1, 2: 2}[1]", 1),
                ("{1: 1, 2: 2}[2]", 2),
                # Do I want this??
                # ("[1, 2, 3][99]", None),
                # ("[1][-1]", None),
                # ("{1: 1}[0]", None),
                # ("[][0]", None),
                # ("{}[0]", None),
            ),
        )

    def test_calling_functions(self) -> None:
        run_vm_tests(
            self,
            (
                ("let fivePlusTen = fn() { 5 + 10; };\n fivePlusTen()", 15),
                (
                    (
                        "let fivePlusTen = fn() { 5 + 10; };\n let thenTimesTwo = fn() { fivePlusTen() * 2 }"
                        "thenTimesTwo()"
                    ),
                    30,
                ),
                (
                    (
                        "let one = fn() { 1; };\n"
                        "let two = fn() { 2; }\n"
                        "one() + two()"
                    ),
                    3,
                ),
                (
                    (
                        "let a = fn() { 1 };\n"
                        "let b = fn() { a() + 1 };\n"
                        "let c = fn() { b() + 1 };\n"
                        "c()"
                    ),
                    3,
                ),
            ),
        )

    def test_calling_functions_with_arguments_and_bindings(self) -> None:
        run_vm_tests(
            self,
            (
                ("let identity = fn(a) { a; };\n identity(4);", 4),
                ("let sum = fn(a, b) { a + b; };\n sum(1, 2);", 3),
                ("let sum = fn(a, b) { let c = a + b; c; };\n sum(1, 2);", 3),
                (
                    "let sum = fn(a, b) { let c = a + b; c; };\n sum(1, 2) + sum(3, 4);",
                    10,
                ),
                (
                    "let sum = fn(a, b) { let c = a + b; c; };\n let outer = fn() { sum(1, 2) + sum(3, 4); }; \nouter();",
                    10,
                ),
                (
                    (
                        "let globalNum = 10;\n\nlet sum = fn(a, b) { let c = a + b; c + globalNum; };\n\nlet outer = fn() {"
                        "sum(1, 2) + sum(3, 4) + globalNum;};\n\nouter() + globalNum;"
                    ),
                    50,
                ),
            ),
        )

    def test_calling_functions_with_wrong_number_of_arguments(self) -> None:
        test_cases: Sequence[str] = (
            "fn() { 1; }(1);",
            "fn(a) { a; }();",
            "fn(a, b) { a + b; }(2);",
        )

        for input_ in test_cases:
            compiler = compilers.Compiler.new()

            program = utils.parse(input_)
            compiler.compile(program)

            vm_ = vm.VM.from_bytecode(compiler.bytecode())
            try:
                vm_.run()
            except vm.MismatchedNumberOfParams:
                pass
            else:
                self.fail(f"Expected MismatchedNumberOfParams for {input_}")

    def test_calling_functions_with_return(self) -> None:
        run_vm_tests(
            self,
            (
                ("let early = fn() { return 99; return 100; }" "early()", 99),
                ("let early = fn() { return 99; 100; }" "early()", 99),
                ("let regular = fn() { 99; return 100; }" "regular()", 100),
            ),
        )

    def test_calling_functions_with_bindings(self) -> None:
        run_vm_tests(
            self,
            (
                ("let one = fn() { let one = 1; one }; one();", 1),
                (
                    "let oneAndTwo = fn() { let one = 1; let two = 2; one + two; }; oneAndTwo();",
                    3,
                ),
                (
                    (
                        "let oneAndTwo = fn() { let one = 1; let two = 2; one + two };\n"
                        "let threeAndFour = fn() { let three = 3; let four = 4; three + four; };\n"
                        "oneAndTwo() + threeAndFour();"
                    ),
                    10,
                ),
                (
                    (
                        "let firstFoobar = fn() { let foobar = 50; foobar; };\n"
                        "let secondFoobar = fn() { let foobar = 100; foobar; };\n"
                        "firstFoobar() + secondFoobar();"
                    ),
                    150,
                ),
                (
                    (
                        "let globalSeed = 50;\n"
                        "let minusOne = fn() { let num = 1; globalSeed - num; }\n"
                        "let minusTwo = fn() { let num = 2; globalSeed - num; }\n"
                        "minusOne() + minusTwo()"
                    ),
                    97,
                ),
            ),
        )

    @unittest.skip("Fails for some reason in the parser")
    def test_first_class_functions(self) -> None:
        run_vm_tests(
            self,
            (
                (
                    (
                        "let returnsOne = fn() { 1; };\n"
                        "let returnsOneReturner = fn() { returnsOne; }\n"
                        "returnsOneReturner()();"
                    ),
                    1,
                ),
            ),
        )

    def test_builtins(self) -> None:
        with self.subTest("len"):
            run_vm_tests(
                self,
                (
                    ('len("")', 0),
                    ('len("four")', 4),
                    ('len("hello world")', 11),
                    (
                        "len(1)",
                        objects.Error("argument to 'len' not supported, got INTEGER"),
                    ),
                    (
                        'len("one", "two")',
                        objects.Error("wrong number of arguments, got 2, want 1"),
                    ),
                    ("len([1, 2, 3])", 3),
                    ("len([])", 0),
                ),
            )

        with self.subTest("puts"):
            run_vm_tests(self, (('puts("hello", "world!")', None),))

        with self.subTest("first"):
            run_vm_tests(
                self,
                (
                    ("first([1, 2, 3])", 1),
                    ("first([])", None),
                    (
                        "first(1)",
                        objects.Error("argument to 'first' not supported, got INTEGER"),
                    ),
                ),
            )

        with self.subTest("last"):
            run_vm_tests(
                self,
                (
                    ("last([1, 2, 3])", 3),
                    ("last([])", None),
                    (
                        "last(1)",
                        objects.Error("argument to 'last' not supported, got INTEGER"),
                    ),
                ),
            )

        with self.subTest("rest"):
            run_vm_tests(
                self,
                (
                    ("rest([1, 2, 3])", [2, 3]),
                    ("rest([])", []),
                ),
            )

        with self.subTest("push"):
            run_vm_tests(
                self,
                (
                    ("push([], 1)", [1]),
                    (
                        "push(1, 1)",
                        objects.Error(
                            "argument to 'rest' at position 1 not supported, got INTEGER"
                        ),
                    ),
                ),
            )
