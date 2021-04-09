import copy

from hypothesis import given

from symba.base import Expression
from . import strategies


@given(strategies.definite_expressions)
def test_shallow(expression: Expression) -> None:
    result = copy.copy(expression)

    assert result is not expression
    assert result == expression


@given(strategies.definite_expressions)
def test_deep(expression: Expression) -> None:
    result = copy.deepcopy(expression)

    assert result is not expression
    assert result == expression
