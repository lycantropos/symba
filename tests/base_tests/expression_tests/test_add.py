from numbers import Real
from typing import (Tuple,
                    Union)

from hypothesis import given

from symba.base import Expression
from . import strategies


@given(strategies.expressions, strategies.finite_reals_or_expressions)
def test_basic(expression: Expression,
               real_or_expression: Union[Real, Expression]) -> None:
    result = expression + real_or_expression

    assert isinstance(result, Expression)


@given(strategies.summable_expressions_pairs)
def test_commutativity(
        expressions_pair: Tuple[Expression, Expression]
) -> None:
    first, second = expressions_pair

    assert first + second == second + first


@given(strategies.zero_expressions, strategies.reals_or_expressions)
def test_left_neutral_element(
        expression: Expression,
        real_or_expression: Union[Real, Expression]
) -> None:
    assert expression + real_or_expression == real_or_expression


@given(strategies.expressions, strategies.zero_reals_or_expressions)
def test_right_neutral_element(
        expression: Expression,
        real_or_expression: Union[Real, Expression]
) -> None:
    assert expression + real_or_expression == expression


@given(strategies.summable_expressions_triplets)
def test_associativity(
        expressions_triplet: Tuple[Expression, Expression, Expression]
) -> None:
    first, second, third = expressions_triplet

    assert (first + second) + third == first + (second + third)
