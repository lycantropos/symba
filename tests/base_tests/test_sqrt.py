import math
from numbers import Real
from typing import Union

import pytest
from hypothesis import given

from symba.base import (Expression,
                        sqrt)
from . import strategies


@given(strategies.non_negative_reals_or_expressions)
def test_basic(value: Union[Real, Expression]) -> None:
    result = sqrt(value)

    assert isinstance(result, Expression)


@given(strategies.non_negative_reals_or_expressions)
def test_sign(value: Union[Real, Expression]) -> None:
    result = sqrt(value)

    assert result >= 0


@given(strategies.non_negative_reals_or_expressions)
def test_value(value: Union[Real, Expression]) -> None:
    result = sqrt(value)

    assert (result == value == 0
            or value < 1 and result > value
            or result == value == 1
            or result < value
            or result == value == math.inf)


@given(strategies.reals_or_expressions)
def test_round_trip(value: Union[Real, Expression]) -> None:
    assert sqrt(value ** 2) == abs(value)


@given(strategies.negative_reals_or_expressions)
def test_negative_argument(value: Union[Real, Expression]) -> None:
    with pytest.raises(ValueError):
        sqrt(value)
