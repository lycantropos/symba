from numbers import Real
from typing import Union

from hypothesis import given

from symba.base import Expression
from . import strategies


@given(strategies.expressions)
def test_basic(expression: Expression) -> None:
    result = abs(expression)

    assert isinstance(result, Expression)


@given(strategies.expressions)
def test_value(expression: Expression) -> None:
    result = abs(expression)

    assert result >= 0


@given(strategies.expressions)
def test_idempotence(expression: Expression) -> None:
    result = abs(expression)

    assert abs(result) == result


@given(strategies.expressions, strategies.expressions)
def test_mul_operand(expression: Expression,
                     real_or_expression: Expression) -> None:
    result = abs(expression * real_or_expression)

    assert result == abs(expression) * abs(real_or_expression)


@given(strategies.expressions, strategies.non_zero_reals_or_expressions)
def test_truediv_operand(expression: Expression,
                         real_or_expression: Expression) -> None:
    result = abs(expression / real_or_expression)

    assert result == abs(expression) / abs(real_or_expression)


@given(strategies.reals_or_expressions, strategies.non_zero_expressions)
def test_rtruediv_operand(real_or_expression: Union[Real, Expression],
                          expression: Expression) -> None:
    result = abs(real_or_expression / expression)

    assert result == abs(real_or_expression) / abs(expression)
