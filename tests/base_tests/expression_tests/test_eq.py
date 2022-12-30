from hypothesis import given

from symba.base import Expression
from tests.utils import (equivalence,
                         implication)
from . import strategies


@given(strategies.expressions)
def test_reflexivity(expression: Expression) -> None:
    assert expression == expression


@given(strategies.expressions, strategies.expressions)
def test_symmetry(first: Expression, second: Expression) -> None:
    assert equivalence(first == second, second == first)


@given(strategies.expressions, strategies.expressions, strategies.expressions)
def test_transitivity(first: Expression,
                      second: Expression,
                      third: Expression) -> None:
    assert implication(first == second and second == third, first == third)


@given(strategies.expressions, strategies.expressions)
def test_connection_with_inequality(first: Expression,
                                    second: Expression) -> None:
    assert equivalence(not first == second, first != second)
