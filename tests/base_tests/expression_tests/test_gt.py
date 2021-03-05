from hypothesis import given

from symba.base import Expression
from tests.utils import (equivalence,
                         implication)
from . import strategies


@given(strategies.expressions)
def test_irreflexivity(expression: Expression) -> None:
    assert not expression > expression


@given(strategies.expressions, strategies.expressions, )
def test_asymmetry(first_expression: Expression,
                   second_expression: Expression) -> None:
    assert implication(first_expression > second_expression,
                       not second_expression > first_expression)


@given(strategies.expressions, strategies.expressions, strategies.expressions)
def test_transitivity(first_expression: Expression,
                      second_expression: Expression,
                      third_expression: Expression) -> None:
    assert implication(first_expression > second_expression > third_expression,
                       first_expression > third_expression)


@given(strategies.expressions, strategies.expressions)
def test_equivalents(first_expression: Expression,
                     second_expression: Expression) -> None:
    result = first_expression > second_expression

    assert equivalence(result, second_expression < first_expression)
    assert equivalence(result,
                       second_expression <= first_expression
                       != second_expression)
    assert equivalence(result,
                       first_expression >= second_expression
                       != first_expression)