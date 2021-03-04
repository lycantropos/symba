import math

from hypothesis import given

from symba.base import Expression
from . import strategies


@given(strategies.expressions)
def test_reflexivity(expression: Expression) -> None:
    result = math.floor(expression)

    assert isinstance(result, int)


@given(strategies.expressions)
def test_value(expression: Expression) -> None:
    result = math.floor(expression)

    assert result <= expression
    assert result > expression - 1
