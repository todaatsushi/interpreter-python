from __future__ import annotations

import unittest

from interpreter import lexers, objects, parsers, evaluate


def test_self_evaluating_object(
    tc: unittest.TestCase,
    expected_class: type[objects.Object],
    obj: objects.Object,
    expected: object,
) -> None:
    tc.assertIsInstance(obj, expected_class)
    assert isinstance(obj, expected_class)

    tc.assertEqual(obj.value, expected, f"{obj.value} vs {expected}")


def get_object(code: str) -> objects.Object:
    lexer = lexers.Lexer.new(code)
    parser = parsers.Parser.new(lexer)
    program = parser.parse_program()
    return evaluate.node(program)


class TestSelfEvaluating(unittest.TestCase):
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
        )

        for code, expected in test_cases:
            actual = get_object(code)
            test_self_evaluating_object(self, objects.Integer, actual, expected)
