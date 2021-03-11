from numbers import Real

import pytest
from hypothesis import given

from symba.base import (Expression,
                        sqrt)
from . import strategies


@given(strategies.non_negative_reals_or_expressions)
def test_basic(value: Real) -> None:
    result = sqrt(value)

    assert isinstance(result, Expression)


@given(strategies.non_negative_reals_or_expressions)
def test_sign(value: Real) -> None:
    result = sqrt(value)

    assert result >= 0


@given(strategies.non_negative_reals_or_expressions)
def test_value(value: Real) -> None:
    result = sqrt(value)

    assert (result == value == 0
            or value < 1 and result > value
            or result == value == 1
            or result < value)


@given(strategies.negative_reals_or_expressions)
def test_negative_argument(value: Real) -> None:
    with pytest.raises(ValueError):
        sqrt(value)
