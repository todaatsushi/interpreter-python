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
        case _:
            logger.error(f"Unhandled type: {type(to_eval)}")
            raise NotImplementedError


def statements(statements_: list[ast.Statement]) -> objects.Object:
    result: objects.Object | None = None
    for statement in statements_:
        result = node(statement)

    assert result is not None
    return result
