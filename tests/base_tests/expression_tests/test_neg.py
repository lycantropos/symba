from numbers import Real
from typing import Union

from hypothesis import given

from symba.base import Expression
from . import strategies


@given(strategies.expressions)
def test_basic(expression: Expression) -> None:
    result = -expression

    assert isinstance(result, Expression)


@given(strategies.expressions)
def test_involution(expression: Expression) -> None:
    result = -expression

    assert -result == expression


@given(strategies.expressions, strategies.reals_or_expressions)
def test_add_operand(expression: Expression,
                     real_or_expression: Expression) -> None:
    result = -(expression + real_or_expression)

    assert result == (-expression) + (-real_or_expression)


@given(strategies.expressions, strategies.expressions)
def test_sub_operand(expression: Expression,
                     real_or_expression: Union[Real, Expression]) -> None:
    result = -(expression - real_or_expression)

    assert result == (-expression) - (-real_or_expression)


@given(strategies.expressions, strategies.expressions)
def test_mul_operand(expression: Expression,
                     real_or_expression: Expression) -> None:
    result = -(expression * real_or_expression)

    assert (result == (-expression) * real_or_expression
            == expression * (-real_or_expression))


@given(strategies.expressions, strategies.non_zero_reals_or_expressions)
def test_truediv_operand(expression: Expression,
                         real_or_expression: Expression) -> None:
    result = -(expression / real_or_expression)

    assert (result == (-expression) / real_or_expression
            == expression / (-real_or_expression))


@given(strategies.reals_or_expressions, strategies.non_zero_expressions)
def test_rtruediv_operand(real_or_expression: Union[Real, Expression],
                          expression: Expression) -> None:
    result = -(real_or_expression / expression)

    assert (result == (-real_or_expression) / expression
            == real_or_expression / (-expression))
