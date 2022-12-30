from numbers import Real
from typing import (Tuple,
                    Union)

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


@given(strategies.summable_expressions_with_reals_or_expressions)
def test_add_operand(expression_with_real_or_expression
                     : Tuple[Expression, Union[Real, Expression]]) -> None:
    expression, real_or_expression = expression_with_real_or_expression

    result = -(expression + real_or_expression)

    assert result == (-expression) + (-real_or_expression)


@given(strategies
       .subtractable_expressions_with_reals_or_expressions)
def test_sub_operand(expression_with_real_or_expression
                     : Tuple[Expression, Union[Real, Expression]]
                     ) -> None:
    expression, real_or_expression = expression_with_real_or_expression

    result = -(expression - real_or_expression)

    assert result == (-expression) - (-real_or_expression)


@given(strategies
       .definitely_multipliable_expressions_with_reals_or_expressions)
def test_mul_operand(expression_with_real_or_expression
                     : Tuple[Expression, Union[Real, Expression]]
                     ) -> None:
    expression, real_or_expression = expression_with_real_or_expression

    result = -(expression * real_or_expression)

    assert (result == (-expression) * real_or_expression
            == expression * (-real_or_expression))


@given(strategies.dividable_expressions_with_reals_or_expressions)
def test_truediv_operand(expression_with_real_or_expression
                         : Tuple[Expression, Union[Real, Expression]]
                         ) -> None:
    expression, real_or_expression = expression_with_real_or_expression

    result = -(expression / real_or_expression)

    assert (result == (-expression) / real_or_expression
            == expression / (-real_or_expression))


@given(strategies.dividable_reals_or_expressions_with_expressions)
def test_rtruediv_operand(real_or_expression_with_expression
                          : Tuple[Union[Real, Expression], Expression]
                          ) -> None:
    real_or_expression, expression = real_or_expression_with_expression

    result = -(real_or_expression / expression)

    assert (result == (-real_or_expression) / expression
            == real_or_expression / (-expression))
