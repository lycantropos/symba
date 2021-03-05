from fractions import Fraction
from typing import Optional

from hypothesis import given

from symba.base import Expression
from symba.core.utils import BASE
from . import strategies


@given(strategies.expressions, strategies.digits_counts)
def test_basic(expression: Expression, digits_count: Optional[int]) -> None:
    result = round(expression, digits_count)

    assert isinstance(result, int if digits_count is None else Fraction)


@given(strategies.expressions, strategies.digits_counts)
def test_value(expression: Expression, digits_count: Optional[int]) -> None:
    result = round(expression, digits_count)

    assert ((result >= int(expression)
             if expression > 0
             else result <= int(expression))
            if digits_count is None
            else result == (round(expression * BASE ** digits_count)
                            / BASE ** digits_count))
