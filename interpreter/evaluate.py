from __future__ import annotations

import logging

from interpreter import ast, environment, objects


logger = logging.getLogger(__name__)


def node(to_eval: ast.Node, env: environment.Environment) -> objects.Object | None:
    match type(to_eval):
        case ast.Program:
            assert isinstance(to_eval, ast.Program)
            return program(to_eval, env)
        case ast.BlockStatement:
            assert isinstance(to_eval, ast.BlockStatement)
            return block_statement(to_eval, env)
        case ast.ExpressionStatement:
            assert isinstance(to_eval, ast.ExpressionStatement) and to_eval.expression
            return node(to_eval.expression, env)
        case ast.IntegerLiteral:
            assert isinstance(to_eval, ast.IntegerLiteral)
            return objects.Integer(value=to_eval.value)
        case ast.BooleanLiteral:
            assert isinstance(to_eval, ast.BooleanLiteral)
            if to_eval.value:
                return objects.TRUE
            return objects.FALSE
        case ast.Identifier:
            assert isinstance(to_eval, ast.Identifier)
            return identifier(to_eval, env)
        case ast.StringLiteral:
            assert isinstance(to_eval, ast.StringLiteral)
            return objects.String(value=to_eval.value)
        case ast.Prefix:
            assert isinstance(to_eval, ast.Prefix) and to_eval.right

            value = node(to_eval.right, env)
            assert value
            if value.type == objects.ObjectType.ERROR:
                return value
            return prefix_expression(to_eval.operator, value)
        case ast.Infix:
            assert isinstance(to_eval, ast.Infix) and to_eval.right and to_eval.left

            left = node(to_eval.left, env)
            assert left
            if left.type == objects.ObjectType.ERROR:
                return left
            right = node(to_eval.right, env)
            assert right
            if right.type == objects.ObjectType.ERROR:
                return right

            return infix_expression(left, to_eval.operator, right)
        case ast.If:
            assert isinstance(to_eval, ast.If)
            return if_expression(to_eval, env)
        case ast.Return:
            assert isinstance(to_eval, ast.Return)
            value = node(to_eval.value, env)
            assert value
            if value.type == objects.ObjectType.ERROR:
                return value
            return objects.Return(value=value)
        case ast.Let:
            assert isinstance(to_eval, ast.Let)
            value = node(to_eval.value, env)
            assert value
            if value.type == objects.ObjectType.ERROR:
                return value

            env.set(to_eval.name.value, value)
        case ast.FunctionLiteral:
            assert isinstance(to_eval, ast.FunctionLiteral)
            params = to_eval.parameters
            body = to_eval.body
            assert body
            return objects.Function(body, env, params)
        case ast.Call:
            assert isinstance(to_eval, ast.Call)
            func = node(to_eval.function, env)
            assert func

            args = expressions(to_eval.arguments, env)
            if len(args) == 1 and args[0].type == objects.ObjectType.ERROR:
                return args[0]
            return function(func, args)
        case _:
            logger.error(f"Unhandled type: {type(to_eval)}")
            raise NotImplementedError


def program(
    program: ast.Program, env: environment.Environment
) -> objects.Object | None:
    result: objects.Object | None = None
    for statement in program.statements:
        result = node(statement, env)

        if isinstance(result, objects.Return):
            return result.value
        elif isinstance(result, objects.Error):
            return result

    return result


def block_statement(
    block: ast.BlockStatement, env: environment.Environment
) -> objects.Object | None:
    result: objects.Object | None = None
    for statement in block.statements:
        result = node(statement, env)
        assert result

        if result.type in (objects.ObjectType.RETURN, objects.ObjectType.ERROR):
            return result

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


def if_expression(expression: ast.If, env: environment.Environment) -> objects.Object:
    condition = node(expression.condition, env)
    assert condition
    if condition.type == objects.ObjectType.ERROR:
        return condition
    elif is_truthy(condition) and expression.consequence:
        value = node(expression.consequence, env)
        assert value
        return value
    elif expression.alternative is not None:
        value = node(expression.alternative, env)
        assert value
        return value
    else:
        return objects.NULL


def identifier(iden: ast.Identifier, env: environment.Environment) -> objects.Object:
    value, ok = env.get(iden.value)
    if not ok:
        return objects.Error(
            message=f"{objects.ErrorTypes.MISSING_IDENTIFER}: {iden.value}"
        )
    assert value is not None
    return value


def expressions(
    exps: list[ast.Expression], env: environment.Environment
) -> list[objects.Object]:
    result: list[objects.Object] = []
    for expression in exps:
        evaluated_expression = node(expression, env)
        if (
            evaluated_expression
            and evaluated_expression.type == objects.ObjectType.ERROR
        ):
            return [evaluated_expression]
        if evaluated_expression:
            result.append(evaluated_expression)
    return result


def extended_function_env(
    function: objects.Function, parameters: list[objects.Object]
) -> environment.Environment:
    env = environment.Environment.new_enclosed(function.env)
    for i, parameter in enumerate(function.parameters):
        env.set(str(parameter.value), parameters[i])
    return env


def function(func: objects.Object, arguments: list[objects.Object]) -> objects.Object:
    if not isinstance(func, objects.Function):
        return objects.Error(
            f"{objects.ErrorTypes.NOT_A_FUNC}: {func} - {', '.join([str(arg) for arg in arguments])}"
        )
    env = extended_function_env(func, arguments)
    evaluated = node(func.body, env)
    assert evaluated
    if isinstance(evaluated, objects.Return):
        return evaluated.value
    return evaluated
