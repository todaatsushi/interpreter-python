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

    tc.assertEqual(obj.value, expected)


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
