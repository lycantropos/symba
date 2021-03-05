from numbers import Real
from typing import Union

from hypothesis import given

from symba.base import Expression
from . import strategies


@given(strategies.expressions, strategies.reals_or_expressions)
def test_basic(expression: Expression,
               real_or_expression: Union[Real, Expression]) -> None:
    result = expression * real_or_expression

    assert isinstance(result, Expression)


@given(strategies.expressions, strategies.expressions)
def test_commutativity(first_expression: Expression,
                       second_expression: Expression) -> None:
    result = first_expression * second_expression

    assert result == second_expression * first_expression


@given(strategies.unary_expressions, strategies.reals_or_expressions)
def test_left_neutral_element(expression: Expression,
                              real_or_expression: Union[Real, Expression]
                              ) -> None:
    result = expression * real_or_expression

    assert result == real_or_expression


@given(strategies.expressions, strategies.unary_reals_or_expressions)
def test_right_neutral_element(expression: Expression,
                               real_or_expression: Union[Real, Expression]
                               ) -> None:
    result = expression * real_or_expression

    assert result == expression


@given(strategies.expressions, strategies.expressions, strategies.expressions)
def test_associativity(first_expression: Expression,
                       second_expression: Expression,
                       third_expression: Expression) -> None:
    assert ((first_expression * second_expression) * third_expression
            == first_expression * (second_expression * third_expression))
