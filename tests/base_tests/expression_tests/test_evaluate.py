from numbers import Real

from hypothesis import given

from symba.base import Expression
from . import strategies


@given(strategies.definite_expressions)
def test_basic(expression: Expression) -> None:
    result = expression.evaluate()

    assert isinstance(result, Real)


@given(strategies.definite_expressions)
def test_commutation_with_abs(expression: Expression) -> None:
    result = expression.evaluate()

    assert abs(result) == abs(expression).evaluate()


@given(strategies.definite_expressions)
def test_commutation_with_neg(expression: Expression) -> None:
    result = expression.evaluate()

    assert -result == (-expression).evaluate()
