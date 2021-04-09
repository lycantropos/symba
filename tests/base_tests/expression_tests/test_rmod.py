from numbers import Real

from hypothesis import given

from symba.base import Expression
from . import strategies


@given(strategies.finite_reals, strategies.finite_non_zero_expressions)
def test_basic(real: Real, expression: Expression) -> None:
    result = real % expression

    assert isinstance(result, Expression)
