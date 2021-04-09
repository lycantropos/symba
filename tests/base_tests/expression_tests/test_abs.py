from numbers import Real
from typing import Tuple, Union

from hypothesis import given

from symba.base import Expression
from . import strategies


@given(strategies.definite_expressions)
def test_basic(expression: Expression) -> None:
    result = abs(expression)

    assert isinstance(result, Expression)


@given(strategies.definite_expressions)
def test_value(expression: Expression) -> None:
    result = abs(expression)

    assert result >= 0


@given(strategies.finite_expressions)
def test_idempotence(expression: Expression) -> None:
    result = abs(expression)

    assert abs(result) == result


@given(strategies.definite_expressions, strategies.definite_expressions)
def test_mul_operand(expression: Expression,
                     real_or_expression: Expression) -> None:
    result = abs(expression * real_or_expression)

    assert result == abs(expression) * abs(real_or_expression)


@given(strategies.definitely_dividable_expressions_with_reals_or_expressions)
def test_truediv_operand(expression_with_real_or_expression
                         : Tuple[Expression, Union[Real, Expression]]) -> None:
    expression, real_or_expression = expression_with_real_or_expression
    result = abs(expression / real_or_expression)

    assert result == abs(expression) / abs(real_or_expression)


@given(strategies.definitely_dividable_reals_or_expressions_with_expressions)
def test_rtruediv_operand(real_or_expression_with_expression
                          : Tuple[Union[Real, Expression], Expression]
                          ) -> None:
    real_or_expression, expression = real_or_expression_with_expression
    result = abs(real_or_expression / expression)

    assert result == abs(real_or_expression) / abs(expression)
