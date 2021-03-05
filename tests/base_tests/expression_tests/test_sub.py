from numbers import Real
from typing import Union

from hypothesis import given

from symba.base import Expression
from tests.utils import equivalence
from . import strategies


@given(strategies.expressions, strategies.reals_or_expressions)
def test_basic(expression: Expression,
               real_or_expression: Union[Real, Expression]) -> None:
    result = expression - real_or_expression

    assert isinstance(result, Expression)


@given(strategies.expressions)
def test_self_inverse(expression: Expression) -> None:
    result = expression - expression

    assert result == 0


@given(strategies.expressions, strategies.expressions)
def test_commutative_case(first_expression: Expression,
                          second_expression: Expression) -> None:
    result = first_expression - second_expression

    assert equivalence(result == second_expression - first_expression,
                       first_expression == second_expression)


@given(strategies.expressions, strategies.zero_reals_or_expressions)
def test_right_neutral_element(expression: Expression,
                               real_or_expression: Union[Real, Expression]
                               ) -> None:
    result = expression - real_or_expression

    assert result == expression


@given(strategies.expressions, strategies.reals_or_expressions,
       strategies.reals_or_expressions)
def test_add_subtrahend(first_expression: Expression,
                        second_expression: Expression,
                        third_expression: Expression) -> None:
    result = first_expression - (second_expression + third_expression)

    assert result == (first_expression - second_expression - third_expression)
