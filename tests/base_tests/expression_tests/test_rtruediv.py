from numbers import Real
from typing import Union

from hypothesis import given

from symba.base import Expression
from . import strategies


@given(strategies.non_zero_reals_or_expressions, strategies.expressions)
def test_basic(real_or_expression: Union[Real, Expression],
               expression: Expression) -> None:
    result = real_or_expression / expression

    assert isinstance(result, Expression)


@given(strategies.reals_or_expressions, strategies.unary_expressions)
def test_right_neutral_element(real_or_expression: Union[Real, Expression],
                               expression: Expression) -> None:
    result = real_or_expression / expression

    assert result == real_or_expression


@given(strategies.reals_or_expressions, strategies.reals_or_expressions,
       strategies.non_zero_expressions)
def test_add_dividend(first_real_or_expression: Union[Real, Expression],
                      second_real_or_expression: Union[Real, Expression],
                      expression: Expression) -> None:
    result = ((first_real_or_expression + second_real_or_expression)
              / expression)

    assert result == ((first_real_or_expression / expression)
                      + (second_real_or_expression / expression))


@given(strategies.reals_or_expressions, strategies.expressions,
       strategies.non_zero_expressions)
def test_sub_dividend(first_real_or_expression: Union[Real, Expression],
                      second_real_or_expression: Union[Real, Expression],
                      expression: Expression) -> None:
    result = ((first_real_or_expression - second_real_or_expression)
              / expression)

    assert result == ((first_real_or_expression / expression)
                      - (second_real_or_expression / expression))
