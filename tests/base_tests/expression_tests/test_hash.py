from hypothesis import given

from symba.base import Expression
from tests.utils import implication
from . import strategies


@given(strategies.expressions)
def test_basic(expression: Expression) -> None:
    result = hash(expression)

    assert isinstance(result, int)


@given(strategies.expressions)
def test_determinism(expression: Expression) -> None:
    result = hash(expression)

    assert result == hash(expression)


@given(strategies.expressions, strategies.expressions)
def test_connection_with_equality(left_expression: Expression,
                                  right_expression: Expression) -> None:
    assert implication(left_expression == right_expression,
                       hash(left_expression) == hash(right_expression))
