from numbers import Real
from typing import (Tuple,
                    Union)

import pytest
from hypothesis import given

from symba.base import Expression
from . import strategies


@given(strategies.reals_or_expressions, strategies.non_zero_finite_expressions)
def test_basic(real_or_expression: Union[Real, Expression],
               expression: Expression) -> None:
    result = real_or_expression * expression

    assert isinstance(result, Expression)


@given(strategies
       .definitely_multipliable_expressions_with_reals_or_expressions)
def test_connection_with_mul(expression_with_real_or_expression
                             : Tuple[Expression, Union[Real, Expression]]
                             ) -> None:
    expression, real_or_expression = expression_with_real_or_expression

    result = real_or_expression * expression

    assert result == expression * real_or_expression


@given(strategies.infinite_reals_or_expressions, strategies.zero_expressions)
def test_infinity_by_zero(
        real_or_expression: Union[Real, Expression],
        expression: Expression
) -> None:
    with pytest.raises(ArithmeticError):
        real_or_expression * expression
