from __future__ import annotations

import unittest

from monkey.interpreter import environment, lexers, objects, parsers, evaluate


def test_self_evaluating_object(
    tc: unittest.TestCase,
    expected_class: type[objects.Object],
    obj: objects.Object,
    expected: object,
) -> None:
    tc.assertIsInstance(obj, expected_class)
    assert isinstance(obj, expected_class)

    tc.assertEqual(obj.value, expected, f"{obj.value} vs {expected}")


def test_error_object(tc: unittest.TestCase, obj: objects.Object, message: str) -> None:
    tc.assertIsInstance(obj, objects.Error)
    assert isinstance(obj, objects.Error)

    tc.assertEqual(obj.message, message)


def get_object(code: str) -> objects.Object:
    lexer = lexers.Lexer.new(code)
    parser = parsers.Parser.new(lexer)
    program = parser.parse_program()
    result = evaluate.node(program, environment.Environment())
    assert result
    return result


class TestSelfEvaluating(unittest.TestCase):
    def test_evalutates_string(self) -> None:
        test_cases: tuple[tuple[str, str], ...] = (
            ('"Hey nazo";', "Hey nazo"),
            ('"";', ""),
            ('"Chef " + "Nazo";', "Chef Nazo"),
        )

        for code, expected in test_cases:
            actual = get_object(code)
            test_self_evaluating_object(self, objects.String, actual, expected)

    def test_evaluates_integers(self) -> None:
        test_cases: tuple[tuple[str, int], ...] = (
            ("5", 5),
            ("10", 10),
        )

        for code, expected in test_cases:
            actual = get_object(code)
            test_self_evaluating_object(self, objects.Integer, actual, expected)

    def test_evaluates_booleans(self) -> None:
        test_cases: tuple[tuple[str, bool], ...] = (
            ("true", True),
            ("false", False),
        )

        for code, expected in test_cases:
            actual = get_object(code)
            test_self_evaluating_object(self, objects.Boolean, actual, expected)
            self.assertIs(actual, objects.TRUE if expected else objects.FALSE)

    def test_evaluates_exclaimation_mark(self) -> None:
        test_cases: tuple[tuple[str, bool], ...] = (
            ("!true", False),
            ("!false", True),
            ("!5", False),
            ("!!true", True),
            ("!!false", False),
            ("!!5", True),
        )

        for code, expected in test_cases:
            actual = get_object(code)
            test_self_evaluating_object(self, objects.Boolean, actual, expected)

    def test_evaluates_minus_prefix(self) -> None:
        test_cases: tuple[tuple[str, int], ...] = (
            ("5", 5),
            ("10", 10),
            ("-5", -5),
            ("-10", -10),
        )

        for code, expected in test_cases:
            actual = get_object(code)
            test_self_evaluating_object(self, objects.Integer, actual, expected)

    def test_evaluates_infix_expressions(self) -> None:
        test_cases: tuple[tuple[str, int], ...] = (
            ("5", 5),
            ("10", 10),
            ("-5", -5),
            ("-10", -10),
            ("5 + 5 + 5 + 5 - 10", 10),
            ("2 * 2 * 2 * 2 * 2", 32),
            ("-50 + 100 + -50", 0),
            ("5 * 2 + 10", 20),
            ("5 + 2 * 10", 25),
            ("20 + 2 * -10", 0),
            ("50 / 2 * 2 + 10", 60),
            ("2 * (5 + 10)", 30),
            ("3 * 3 * 3 + 10", 37),
            ("3 * (3 * 3) + 10", 37),
            ("(5 + 10 * 2 + 15 / 3) * 2 + -10", 50),
        )

        for code, expected in test_cases:
            actual = get_object(code)
            test_self_evaluating_object(self, objects.Integer, actual, expected)

    def test_evalutes_boolean_expressions(self) -> None:
        test_cases: tuple[tuple[str, bool], ...] = (
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
        )

        for code, expected in test_cases:
            actual = get_object(code)
            test_self_evaluating_object(self, objects.Boolean, actual, expected)
            self.assertIs(actual, objects.TRUE if expected else objects.FALSE)

    def test_evaluates_simple_if_else(self) -> None:
        test_cases: tuple[tuple[str, int | None], ...] = (
            ("if (true) { 10 }", 10),
            ("if (false) { 10 }", None),
            ("if (1) { 10 }", 10),
            ("if (1 < 2) { 10 }", 10),
            ("if (1 > 2) { 10 }", None),
            ("if (1 > 2) { 10 } else { 20 }", 20),
            ("if (1 < 2) { 10 } else { 20 }", 10),
        )
        for code, expected in test_cases:
            actual = get_object(code)
            expected_class = objects.Integer
            if expected is None:
                expected_class = objects.Null
            test_self_evaluating_object(self, expected_class, actual, expected)

            if expected is None:
                self.assertIs(actual, objects.NULL)

    def test_evaluates_return(self) -> None:
        test_cases: tuple[tuple[str, int], ...] = (
            ("return 10;", 10),
            ("return 10; 9;", 10),
            ("return 2 * 5; 9;", 10),
            ("9; return 2 * 5; 9;", 10),
            (
                """
             if (10 > 1) {
                  if (10 > 1) {
                    return 10;
             }
             return 1; }
             """,
                10,
            ),
        )

        for code, expected in test_cases:
            actual = get_object(code)
            test_self_evaluating_object(self, objects.Integer, actual, expected)

    def test_evaluates_let(self) -> None:
        test_cases: tuple[tuple[str, int], ...] = (
            ("let a = 5; a;", 5),
            ("let a = 5 * 5; a;", 25),
            ("let a = 5; let b = a; b;", 5),
            ("let a = 5; let b = a; let c = a + b + 5; c;", 15),
        )

        for code, expected in test_cases:
            actual = get_object(code)
            test_self_evaluating_object(self, objects.Integer, actual, expected)

    def test_evaluates_array_literals(self) -> None:
        test_cases: tuple[tuple[str, int | str | list[int]], ...] = (
            ("[1, 2 * 2, 3 + 3]", [1, 4, 6]),
            ("[1, 2, 3][0]", 1),
            ("[1, 2, 3][1]", 2),
            ("[1, 2, 3][2]", 3),
            ("let i = 0; [1][i];", 1),
            ("[1, 2, 3][1 + 1];", 3),
            ("let myArray = [1, 2, 3]; myArray[2];", 3),
            ("let myArray = [1, 2, 3]; myArray[0] + myArray[1] + myArray[2];", 6),
            ("let myArray = [1, 2, 3]; let i = myArray[0]; myArray[i]", 2),
            ("[1, 2, 3][3]", "invalid index: index must be between 0 and 2 inclusive"),
            ("[1, 2, 3][-1]", "invalid index: index must be between 0 and 2 inclusive"),
        )

        for code, expected in test_cases:
            with self.subTest(code):
                obj = get_object(code)

                if isinstance(expected, str):
                    test_error_object(self, obj, expected)
                else:
                    if isinstance(expected, list):
                        self.assertIsInstance(obj, objects.Array)
                        assert isinstance(obj, objects.Array)
                        self.assertEqual(len(obj.items), len(expected))
                        for i, expected in enumerate(expected):
                            actual = obj.items[i]
                            test_self_evaluating_object(
                                self, objects.Integer, actual, expected
                            )
                    else:
                        self.assertIsInstance(obj, objects.Integer)
                        assert isinstance(obj, objects.Integer)

                        test_self_evaluating_object(
                            self, objects.Integer, obj, expected
                        )


class TestErrorHandling(unittest.TestCase):
    def test_evaluates_type_mismatch_error(self) -> None:
        test_cases: tuple[tuple[str, str], ...] = (
            ("5 + true", "type mismatch: INTEGER + BOOLEAN"),
            ("5 + true; 5;", "type mismatch: INTEGER + BOOLEAN"),
        )

        for code, expected in test_cases:
            actual = get_object(code)
            test_error_object(self, actual, expected)

    def test_evaluates_unknown_operator_error(self) -> None:
        test_cases: tuple[tuple[str, str], ...] = (
            ("-true", "unknown operator: -BOOLEAN"),
            ("true + false;", "unknown operator: BOOLEAN + BOOLEAN"),
            ("5; true + false; 5", "unknown operator: BOOLEAN + BOOLEAN"),
            ("if (10 > 1) { true + false; }", "unknown operator: BOOLEAN + BOOLEAN"),
            (
                """
                if (10 > 1) {
                    if (10 > 1) {
                        return true + false;
                    }
                    return 1;
                }
                """,
                "unknown operator: BOOLEAN + BOOLEAN",
            ),
        )

        for code, expected in test_cases:
            actual = get_object(code)
            test_error_object(self, actual, expected)

    def test_evaluates_missing_identifer(self) -> None:
        code = "foobar"
        expected = "missing identifier: foobar"

        actual = get_object(code)
        test_error_object(self, actual, expected)

    def test_evaluates_unhashable_index_key(self) -> None:
        code = '{"name": "Monkey"}[fn(x) { x }];'
        expected = "invalid index: can't index HASH with FUNCTION"

        actual = get_object(code)
        test_error_object(self, actual, expected)

    def test_evaluates_hash_key_error(self) -> None:
        code = '{"name": "Monkey"}["nazo"];'
        expected = 'key error: no value with key "nazo"'

        actual = get_object(code)
        test_error_object(self, actual, expected)


class TestFunctions(unittest.TestCase):
    def test_evaluates_function_object(self) -> None:
        code = "fn(x) { x + 2; };"
        actual = get_object(code)

        self.assertIsInstance(actual, objects.Function)
        assert isinstance(actual, objects.Function)

        self.assertEqual(len(actual.parameters), 1)
        self.assertEqual(str(actual.parameters[0]), "x")
        self.assertEqual(str(actual.body), "(x + 2)")

    def test_evaluates_function_application(self) -> None:
        test_cases: tuple[tuple[str, int], ...] = (
            ("let identity = fn(x) { x; }; identity(5);", 5),
            ("let identity = fn(x) { return x; }; identity(5);", 5),
            ("let double = fn(x) { x * 2; }; double(5);", 10),
            ("let add = fn(x, y) { x + y; }; add(5, 5);", 10),
            ("let add = fn(x, y) { x + y; }; add(5 + 5, add(5, 5));", 20),
            ("fn(x) { x; }(5)", 5),
        )

        for code, expected in test_cases:
            actual = get_object(code)
            test_self_evaluating_object(self, objects.Integer, actual, expected)

    def test_evaluates_closures(self) -> None:
        code = """
        let newAdder = fn(x) {
            fn(y) { x + y };
        };
        let addTwo = newAdder(2);
        addTwo(2);
        """
        actual = get_object(code)
        test_self_evaluating_object(self, objects.Integer, actual, 4)


class TestBuiltinFunctions(unittest.TestCase):
    def test_evaluates_len(self) -> None:
        test_cases: tuple[tuple[str, int], ...] = (
            ("Hello World!", 12),
            ("", 0),
        )

        for value, expected in test_cases:
            code = f'len("{value}");'
            actual = get_object(code)
            test_self_evaluating_object(self, objects.Integer, actual, expected)

    def test_evaluates_len_errors(self) -> None:
        test_cases: tuple[tuple[list[object], str], ...] = (
            ([1], "argument to 'len' not supported, got INTEGER"),
            (['"one"', '"two"'], "wrong number of arguments, got 2, want 1"),
        )

        for call_args, expected in test_cases:
            code = f"len({', '.join(str(arg) for arg in call_args)});"
            actual = get_object(code)
            test_error_object(self, actual, expected)

    def test_evaluates_first(self) -> None:
        test_cases: tuple[tuple[str, object], ...] = (
            ("[1, 2, 3]", 1),
            ("[]", None),
        )

        for input_, expected in test_cases:
            with self.subTest(input_):
                code = f"first({input_})"
                actual = get_object(code)
                if isinstance(expected, int):
                    test_self_evaluating_object(self, objects.Integer, actual, 1)
                elif expected is None:
                    self.assertEqual(actual, objects.NULL)

    def test_evaluates_first_error(self) -> None:
        test_cases: tuple[tuple[str, object], ...] = (
            ("first()", "wrong number of arguments, got 0, want 1"),
            ("first(1, 2, 3)", "wrong number of arguments, got 3, want 1"),
            ('first("hello")', "argument to 'first' not supported, got STRING"),
        )

        for code, expected in test_cases:
            with self.subTest(code):
                actual = get_object(code)
                test_error_object(self, actual, expected)

    def test_evaluates_last(self) -> None:
        test_cases: tuple[tuple[str, object], ...] = (
            ("[1, 2, 3]", 3),
            ("[]", None),
        )

        for input_, expected in test_cases:
            with self.subTest(input_):
                code = f"last({input_})"
                actual = get_object(code)
                if isinstance(expected, int):
                    test_self_evaluating_object(self, objects.Integer, actual, 3)
                elif expected is None:
                    self.assertEqual(actual, objects.NULL)

    def test_evaluates_last_error(self) -> None:
        test_cases: tuple[tuple[str, object], ...] = (
            ("last()", "wrong number of arguments, got 0, want 1"),
            ("last(1, 2, 3)", "wrong number of arguments, got 3, want 1"),
            ('last("hello")', "argument to 'last' not supported, got STRING"),
        )

        for code, expected in test_cases:
            with self.subTest(code):
                actual = get_object(code)
                test_error_object(self, actual, expected)

    def test_evaluates_rest(self) -> None:
        test_cases: tuple[tuple[str, list[int]], ...] = (
            ("[1, 2, 3]", [2, 3]),
            ("[]", []),
        )

        for input_, expected in test_cases:
            with self.subTest(input_):
                code = f"rest({input_})"
                array = get_object(code)

                self.assertIsInstance(array, objects.Array)
                assert isinstance(array, objects.Array)

                actual = [item.value for item in array.items]
                self.assertListEqual(actual, expected)

    def test_evaluates_rest_errors(self) -> None:
        test_cases: tuple[tuple[str, str], ...] = (
            ("rest()", "wrong number of arguments, got 0, want 1"),
            ("rest([1], [1], [1])", "wrong number of arguments, got 3, want 1"),
            ('rest("hello")', "argument to 'rest' not supported, got STRING"),
        )

        for code, expected in test_cases:
            with self.subTest(code):
                actual = get_object(code)
                test_error_object(self, actual, expected)

    def test_evaluates_push(self) -> None:
        test_cases: tuple[tuple[str, list[int | str]], ...] = (
            ("[1, 2, 3], 4", [1, 2, 3, 4]),
            ('[], "hello"', ["hello"]),
        )

        for input_, expected in test_cases:
            with self.subTest(input_):
                code = f"push({input_})"
                array = get_object(code)

                self.assertIsInstance(array, objects.Array)
                assert isinstance(array, objects.Array)

                actual = [item.value for item in array.items]
                self.assertListEqual(actual, expected)

    def test_evaluates_push_errors(self) -> None:
        test_cases: tuple[tuple[str, str], ...] = (
            ("push()", "wrong number of arguments, got 0, want 2"),
            ("push([1])", "wrong number of arguments, got 1, want 2"),
            ("push([1], [1], [1])", "wrong number of arguments, got 3, want 2"),
            (
                'push("hello", 1)',
                "argument to 'rest' at position 1 not supported, got STRING",
            ),
        )

        for code, expected in test_cases:
            with self.subTest(code):
                actual = get_object(code)
                test_error_object(self, actual, expected)


class TestHashing(unittest.TestCase):
    def test_evaluates_same_with_value(self) -> None:
        test_cases: tuple[tuple[object, type[objects.Hashable]], ...] = (
            ("Nazo de aru", objects.String),
            (10, objects.Integer),
            (True, objects.Boolean),
        )
        for value, class_ in test_cases:
            one = class_(value)  # type: ignore
            two = class_(value)  # type: ignore
            self.assertEqual(one.hash_key(), two.hash_key())

    def test_evaluates_hash(self) -> None:
        code = """
        let two = "two";
        {
           "one": 10 - 9,
           two: 1 + 1,
           "thr" + "ee": 6 / 2,
           4: 4,
           true: 5,
           false: 6
        }
        """
        hash = get_object(code)

        self.assertIsInstance(hash, objects.Hash)
        assert isinstance(hash, objects.Hash)

        expected = {
            objects.String("one").hash_key(): 1,
            objects.String("two").hash_key(): 2,
            objects.String("three").hash_key(): 3,
            objects.Integer(4).hash_key(): 4,
            objects.TRUE.hash_key(): 5,
            objects.FALSE.hash_key(): 6,
        }

        with self.subTest("Num keys"):
            self.assertEqual(len(expected), len(hash.pairs))

        for expected_hash_key, expected_value in expected.items():
            pair = hash.pairs[expected_hash_key]
            with self.subTest(expected_hash_key):
                self.assertEqual(expected_value, pair.value.value)

    def test_evaluates_index_expressions(self) -> None:
        test_cases: tuple[tuple[str, int | None], ...] = (
            ('{"foo": 5}["foo"]', 5),
            ('{"foo": 5}["foo"]', 5),
        )

        for code, expected in test_cases:
            actual = get_object(code)
            if isinstance(expected, int):
                test_self_evaluating_object(self, objects.Integer, actual, expected)
            else:
                self.assertEqual(actual, objects.NULL)
