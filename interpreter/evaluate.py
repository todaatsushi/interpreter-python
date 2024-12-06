from __future__ import annotations

import logging

from interpreter import ast, objects


logger = logging.getLogger(__name__)


def node(to_eval: ast.Node) -> objects.Object:
    match type(to_eval):
        case ast.Program:
            assert isinstance(to_eval, ast.Program)
            return program(to_eval)
        case ast.BlockStatement:
            assert isinstance(to_eval, ast.BlockStatement)
            return block_statement(to_eval)
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

            value = node(to_eval.right)
            if value.type == objects.ObjectType.ERROR:
                return value
            return prefix_expression(to_eval.operator, value)
        case ast.Infix:
            assert isinstance(to_eval, ast.Infix) and to_eval.right and to_eval.left

            left = node(to_eval.left)
            if left.type == objects.ObjectType.ERROR:
                return left
            right = node(to_eval.right)
            if right.type == objects.ObjectType.ERROR:
                return right

            return infix_expression(left, to_eval.operator, right)

        case ast.If:
            assert isinstance(to_eval, ast.If)
            return if_expression(to_eval)
        case ast.Return:
            assert isinstance(to_eval, ast.Return)
            value = node(to_eval.value)
            if value.type == objects.ObjectType.ERROR:
                return value
            return objects.Return(value=value)
        case _:
            logger.error(f"Unhandled type: {type(to_eval)}")
            raise NotImplementedError


def program(program: ast.Program) -> objects.Object:
    result: objects.Object | None = None
    for statement in program.statements:
        result = node(statement)

        if isinstance(result, objects.Return):
            return result.value
        elif isinstance(result, objects.Error):
            return result

    assert result is not None
    return result


def block_statement(block: ast.BlockStatement) -> objects.Object:
    result: objects.Object | None = None
    for statement in block.statements:
        result = node(statement)

        if result.type in (objects.ObjectType.RETURN, objects.ObjectType.ERROR):
            return result

    assert result is not None
    return result


def prefix_expression(operator: str, right: objects.Object) -> objects.Object:
    match operator:
        case "!":
            return exclaimation_mark(right)
        case "-":
            if isinstance(right, objects.Integer):
                return prefix_minus(right)
        case _:
            pass

    return objects.Error(
        message=f"{objects.ErrorTypes.UNKNOWN_OPERATOR}: {operator}{right.type}"
    )


def infix_expression(
    left: objects.Object, operator: str, right: objects.Object
) -> objects.Object:
    match operator:
        case "+":
            return plus(left, right)
        case "-":
            return minus(left, right)
        case "*":
            return multiply(left, right)
        case "/":
            return divide(left, right)
        case "<":
            return less_than(left, right)
        case ">":
            return more_than(left, right)
        case "==":
            return equality(left, right, True)
        case "!=":
            return equality(left, right, False)
        case _:
            return objects.Error(
                message=f"{objects.ErrorTypes.UNKNOWN_OPERATOR}: {left.type} {operator} {right.type}"
            )


def plus(left: objects.Object, right: objects.Object) -> objects.Object:
    if isinstance(left, objects.Integer) and isinstance(right, objects.Integer):
        return objects.Integer(value=left.value + right.value)

    if type(left) is not type(right):
        error_type = objects.ErrorTypes.TYPE_MISMATCH
    else:
        error_type = objects.ErrorTypes.UNKNOWN_OPERATOR
    return objects.Error(message=f"{error_type}: {left.type} + {right.type}")


def minus(left: objects.Object, right: objects.Object) -> objects.Object:
    if isinstance(left, objects.Integer) and isinstance(right, objects.Integer):
        return objects.Integer(value=left.value - right.value)

    if type(left) is not type(right):
        error_type = objects.ErrorTypes.TYPE_MISMATCH
    else:
        error_type = objects.ErrorTypes.UNKNOWN_OPERATOR
    return objects.Error(message=f"{error_type}: {type(left)} - {type(right)}")


def multiply(left: objects.Object, right: objects.Object) -> objects.Object:
    if isinstance(left, objects.Integer) and isinstance(right, objects.Integer):
        return objects.Integer(value=left.value * right.value)

    if type(left) is not type(right):
        error_type = objects.ErrorTypes.TYPE_MISMATCH
    else:
        error_type = objects.ErrorTypes.UNKNOWN_OPERATOR
    return objects.Error(message=f"{error_type}: {type(left)} * {type(right)}")


def divide(left: objects.Object, right: objects.Object) -> objects.Object:
    """
    Note: floor, not true divide
    """
    if isinstance(left, objects.Integer) and isinstance(right, objects.Integer):
        return objects.Integer(value=left.value // right.value)

    if type(left) is not type(right):
        error_type = objects.ErrorTypes.TYPE_MISMATCH
    else:
        error_type = objects.ErrorTypes.UNKNOWN_OPERATOR
    return objects.Error(message=f"{error_type}: {type(left)} / {type(right)}")


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


def less_than(left: objects.Object, right: objects.Object) -> objects.Object:
    if isinstance(left, objects.Integer) and isinstance(right, objects.Integer):
        if left.value < right.value:
            return objects.TRUE
        return objects.FALSE

    if type(left) is not type(right):
        error_type = objects.ErrorTypes.TYPE_MISMATCH
    else:
        error_type = objects.ErrorTypes.UNKNOWN_OPERATOR
    return objects.Error(message=f"{error_type}: {type(left)} < {type(right)}")


def more_than(left: objects.Object, right: objects.Object) -> objects.Object:
    if isinstance(left, objects.Integer) and isinstance(right, objects.Integer):
        if left.value > right.value:
            return objects.TRUE
        return objects.FALSE

    if type(left) is not type(right):
        error_type = objects.ErrorTypes.TYPE_MISMATCH
    else:
        error_type = objects.ErrorTypes.UNKNOWN_OPERATOR
    return objects.Error(message=f"{error_type}: {type(left)} > {type(right)}")


def equality(
    left: objects.Object, right: objects.Object, positive: bool
) -> objects.Object:
    if isinstance(left, objects.Integer) and isinstance(right, objects.Integer):
        result = left.value == right.value
        if not positive:
            result = not result

        if result:
            return objects.TRUE
        return objects.FALSE
    if isinstance(left, objects.Boolean) and isinstance(right, objects.Boolean):
        result = left.value is right.value
        if not positive:
            result = not result

        if result:
            return objects.TRUE
        return objects.FALSE

    operator = "==" if positive else "!="
    if type(left) is not type(right):
        error_type = objects.ErrorTypes.TYPE_MISMATCH
    else:
        error_type = objects.ErrorTypes.UNKNOWN_OPERATOR
    return objects.Error(message=f"{error_type}: {type(left)} {operator} {type(right)}")


def is_truthy(obj: objects.Object) -> bool:
    match obj:
        case objects.NULL:
            return False
        case objects.TRUE:
            return True
        case objects.FALSE:
            return False
        case _:
            return True


def if_expression(expression: ast.If) -> objects.Object:
    condition = node(expression.condition)
    if condition.type == objects.ObjectType.ERROR:
        return condition
    elif is_truthy(condition) and expression.consequence:
        return node(expression.consequence)
    elif expression.alternative is not None:
        return node(expression.alternative)
    else:
        return objects.NULL
