from typing import Tuple

from hypothesis import given

from symba.base import Expression
from tests.utils import (equivalence,
                         implication)
from . import strategies


@given(strategies.expressions)
def test_reflexivity(expression: Expression) -> None:
    assert expression == expression


@given(strategies.expressions_pairs)
def test_symmetry(expressions_pair: Tuple[Expression, Expression]) -> None:
    first_expression, second_expression = expressions_pair

    assert equivalence(first_expression == second_expression,
                       second_expression == first_expression)


@given(strategies.expressions_triplets)
def test_transitivity(expressions_triplet
                      : Tuple[Expression, Expression, Expression]) -> None:
    first_expression, second_expression, third_expression = expressions_triplet

    assert implication(first_expression == second_expression
                       and second_expression == third_expression,
                       first_expression == third_expression)


@given(strategies.expressions_pairs)
def test_connection_with_inequality(expressions_pair
                                    : Tuple[Expression, Expression]) -> None:
    first_expression, second_expression = expressions_pair

    assert equivalence(not first_expression == second_expression,
                       first_expression != second_expression)
