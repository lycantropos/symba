import math
from numbers import Real
from typing import Union

from hypothesis import given

from symba.base import Expression
from . import strategies


@given(strategies.expressions, strategies.non_zero_reals_or_expressions)
def test_basic(expression: Expression,
               expression_or_real: Union[Real, Expression]) -> None:
    result = expression // expression_or_real

    assert isinstance(result, int)


@given(strategies.expressions, strategies.non_zero_reals_or_expressions)
def test_value(expression: Expression,
               expression_or_real: Union[Real, Expression]) -> None:
    result = expression // expression_or_real

    assert (expression % expression_or_real == 0
            and result == expression / expression_or_real
            or result < expression / expression_or_real)


@given(strategies.expressions)
def test_division_by_one(expression: Expression) -> None:
    result = expression // 1

    assert result == math.floor(expression)
