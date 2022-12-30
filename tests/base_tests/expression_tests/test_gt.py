from hypothesis import given

from symba.base import Expression
from tests.utils import (equivalence,
                         implication)
from . import strategies


@given(strategies.expressions)
def test_irreflexivity(expression: Expression) -> None:
    assert not expression > expression


@given(strategies.expressions, strategies.expressions)
def test_asymmetry(first: Expression, second: Expression) -> None:
    assert implication(first > second,
                       not second > first)


@given(strategies.expressions, strategies.expressions,
       strategies.expressions)
def test_transitivity(first: Expression,
                      second: Expression,
                      third: Expression) -> None:
    assert implication(first > second > third, first > third)


@given(strategies.expressions, strategies.expressions)
def test_equivalents(first: Expression, second: Expression) -> None:
    result = first > second

    assert equivalence(result, second < first)
    assert equivalence(result, second <= first != second)
    assert equivalence(result, first >= second != first)
