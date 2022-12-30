from hypothesis import given

from symba.base import Expression
from tests.utils import (equivalence,
                         implication)
from . import strategies


@given(strategies.expressions)
def test_reflexivity(expression: Expression) -> None:
    assert expression <= expression


@given(strategies.expressions, strategies.expressions)
def test_antisymmetry(first: Expression, second: Expression) -> None:
    assert equivalence(first <= second <= first, first == second)


@given(strategies.expressions, strategies.expressions,
       strategies.expressions)
def test_transitivity(first: Expression,
                      second: Expression,
                      third: Expression) -> None:
    assert implication(first <= second <= third, first <= third)


@given(strategies.expressions, strategies.expressions)
def test_equivalents(first: Expression, second: Expression) -> None:
    result = first <= second

    assert equivalence(result, second >= first)
    assert equivalence(result, first < second or first == second)
    assert equivalence(result, second > first or first == second)
