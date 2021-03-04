from hypothesis import given

from symba.base import Expression
from . import strategies


@given(strategies.expressions)
def test_identity(expression: Expression) -> None:
    result = +expression

    assert result == expression
