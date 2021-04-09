import math

from hypothesis import given

from symba.base import Expression
from . import strategies


@given(strategies.finite_expressions)
def test_basic(expression: Expression) -> None:
    result = math.ceil(expression)

    assert isinstance(result, int)


@given(strategies.finite_expressions)
def test_value(expression: Expression) -> None:
    result = math.ceil(expression)

    assert result >= expression
    assert result < expression + 1
