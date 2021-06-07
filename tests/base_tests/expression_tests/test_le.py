from hypothesis import given

from symba.base import Expression
from tests.utils import (equivalence,
                         implication)
from . import strategies


@given(strategies.definite_expressions)
def test_reflexivity(expression: Expression) -> None:
    assert expression <= expression


@given(strategies.definite_expressions, strategies.definite_expressions)
def test_antisymmetry(first: Expression, second: Expression) -> None:
    assert equivalence(first <= second <= first, first == second)


@given(strategies.indefinite_expressions, strategies.expressions)
def test_indefinite(first: Expression, second: Expression) -> None:
    assert not (first <= second or second <= first)


@given(strategies.definite_expressions, strategies.definite_expressions,
       strategies.definite_expressions)
def test_transitivity(first: Expression,
                      second: Expression,
                      third: Expression) -> None:
    assert implication(first <= second <= third, first <= third)


@given(strategies.definite_expressions, strategies.definite_expressions)
def test_equivalents(first: Expression, second: Expression) -> None:
    result = first <= second

    assert equivalence(result, second >= first)
    assert equivalence(result, first < second or first == second)
    assert equivalence(result, second > first or first == second)
