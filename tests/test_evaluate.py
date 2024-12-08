from __future__ import annotations

import unittest

from interpreter import environment, lexers, objects, parsers, evaluate


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
            # ([1], "argument to 'len' not supported, got INTEGER"),
            (['"one"', '"two"'], "wrong number of arguments, got 2, want 1"),
        )

        for call_args, expected in test_cases:
            code = f"len({', '.join(str(arg) for arg in call_args)});"
            actual = get_object(code)
            test_error_object(self, actual, expected)
