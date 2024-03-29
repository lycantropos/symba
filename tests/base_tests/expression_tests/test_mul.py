from numbers import Real
from typing import (Tuple,
                    Union)

import pytest
from hypothesis import given

from symba.base import Expression
from . import strategies


@given(strategies.expressions, strategies.non_zero_finite_reals_or_expressions)
def test_basic(expression: Expression,
               real_or_expression: Union[Real, Expression]) -> None:
    result = expression * real_or_expression

    assert isinstance(result, Expression)


@given(strategies.multipliable_expressions_pairs)
def test_commutativity(
        expressions_pair: Tuple[Expression, Expression]
) -> None:
    first, second = expressions_pair

    assert first * second == second * first


@given(strategies.unary_expressions, strategies.reals_or_expressions)
def test_left_neutral_element(
        expression: Expression,
        real_or_expression: Union[Real, Expression]
) -> None:
    result = expression * real_or_expression

    assert result == real_or_expression


@given(strategies.expressions, strategies.unary_reals_or_expressions)
def test_right_neutral_element(
        expression: Expression,
        real_or_expression: Union[Real, Expression]
) -> None:
    result = expression * real_or_expression

    assert result == expression


@given(strategies.multipliable_expressions_triplets)
def test_associativity(
        expressions_triplet: Tuple[Expression, Expression, Expression]
) -> None:
    first, second, third = expressions_triplet

    assert (first * second) * third == first * (second * third)


@given(strategies.infinite_expressions, strategies.zero_reals_or_expressions)
def test_infinity_by_zero(
        expression: Expression,
        real_or_expression: Union[Real, Expression]
) -> None:
    with pytest.raises(ArithmeticError):
        expression * real_or_expression
