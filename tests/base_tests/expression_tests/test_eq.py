from hypothesis import given

from symba.base import Expression
from tests.utils import (equivalence,
                         implication)
from . import strategies


@given(strategies.expressions)
def test_reflexivity(expression: Expression) -> None:
    assert expression == expression


@given(strategies.expressions, strategies.expressions)
def test_symmetry(first_expression: Expression,
                  second_expression: Expression) -> None:
    assert equivalence(first_expression == second_expression,
                       second_expression == first_expression)


@given(strategies.expressions, strategies.expressions, strategies.expressions)
def test_transitivity(first_expression: Expression,
                      second_expression: Expression,
                      third_expression: Expression) -> None:
    assert implication(first_expression == second_expression
                       and second_expression == third_expression,
                       first_expression == third_expression)


@given(strategies.expressions, strategies.expressions)
def test_connection_with_inequality(first_expression: Expression,
                                    second_expression: Expression) -> None:
    assert equivalence(not first_expression == second_expression,
                       first_expression != second_expression)
