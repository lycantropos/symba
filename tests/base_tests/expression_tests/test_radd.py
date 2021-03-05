from numbers import Real
from typing import Union

from hypothesis import given

from symba.base import Expression
from . import strategies


@given(strategies.reals_or_expressions, strategies.expressions)
def test_basic(real_or_expression: Union[Real, Expression],
               expression: Expression) -> None:
    result = real_or_expression + expression

    assert isinstance(result, Expression)


@given(strategies.reals_or_expressions, strategies.expressions)
def test_connection_with_add(real_or_expression: Union[Real, Expression],
                             expression: Expression) -> None:
    result = real_or_expression + expression

    assert result == expression + real_or_expression
