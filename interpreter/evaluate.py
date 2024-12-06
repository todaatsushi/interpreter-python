from __future__ import annotations

import logging

from interpreter import ast, objects


logger = logging.getLogger(__name__)


def node(to_eval: ast.Node) -> objects.Object:
    match type(to_eval):
        case ast.Program:
            assert isinstance(to_eval, ast.Program)
            return statements(to_eval.statements)
        case ast.ExpressionStatement:
            assert isinstance(to_eval, ast.ExpressionStatement) and to_eval.expression
            return node(to_eval.expression)
        case ast.IntegerLiteral:
            assert isinstance(to_eval, ast.IntegerLiteral)
            return objects.Integer(value=to_eval.value)
        case ast.BooleanLiteral:
            assert isinstance(to_eval, ast.BooleanLiteral)
            if to_eval.value:
                return objects.TRUE
            return objects.FALSE
        case ast.Prefix:
            assert isinstance(to_eval, ast.Prefix) and to_eval.right
            return prefix_expression(to_eval.operator, node(to_eval.right))
        case _:
            logger.error(f"Unhandled type: {type(to_eval)}")
            raise NotImplementedError


def statements(statements_: list[ast.Statement]) -> objects.Object:
    result: objects.Object | None = None
    for statement in statements_:
        result = node(statement)

    assert result is not None
    return result


def prefix_expression(operator: str, right: objects.Object) -> objects.Object:
    match operator:
        case "!":
            return exclaimation_mark(right)
        case "-":
            if isinstance(right, objects.Integer):
                return prefix_minus(right)
            return objects.NULL
        case _:
            logger.error(f"Unhandled for operator: {operator}")
            raise NotImplementedError


def exclaimation_mark(right: objects.Object) -> objects.Object:
    match right:
        case objects.TRUE:
            return objects.FALSE
        case objects.FALSE:
            return objects.TRUE
        case objects.Null:
            return objects.FALSE
        case _:
            return objects.FALSE


def prefix_minus(right: objects.Integer) -> objects.Object:
    return objects.Integer(value=right.value * -1)
