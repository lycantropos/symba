from numbers import Real
from typing import (Tuple,
                    Union)

from hypothesis import given

from symba.base import Expression
from tests.utils import equivalence
from . import strategies


@given(strategies.expressions, strategies.finite_reals_or_expressions)
def test_basic(expression: Expression,
               real_or_expression: Union[Real, Expression]) -> None:
    result = expression - real_or_expression

    assert isinstance(result, Expression)


@given(strategies.finite_expressions)
def test_self_inverse(expression: Expression) -> None:
    result = expression - expression

    assert result == 0


@given(strategies.subtractable_expressions_pairs)
def test_commutative_case(expressions_pair: Tuple[Expression, Expression]
                          ) -> None:
    first, second = expressions_pair

    assert equivalence(first - second == second - first, first == second)


@given(strategies.expressions, strategies.zero_reals_or_expressions)
def test_right_neutral_element(expression: Expression,
                               real_or_expression: Union[Real, Expression]
                               ) -> None:
    assert expression - real_or_expression == expression


@given(strategies.finite_expressions, strategies.finite_reals_or_expressions,
       strategies.finite_reals_or_expressions)
def test_add_subtrahend(first: Expression,
                        second: Expression,
                        third: Expression) -> None:
    assert first - (second + third) == (first - second - third)
