import math
from numbers import Real
from typing import Union

from hypothesis import given

from symba.base import Expression
from . import strategies


@given(strategies.finite_expressions,
       strategies.finite_non_zero_reals_or_expressions)
def test_basic(expression: Expression,
               expression_or_real: Union[Real, Expression]) -> None:
    result = expression % expression_or_real

    assert isinstance(result, Expression)


@given(strategies.finite_expressions,
       strategies.finite_non_zero_reals_or_expressions)
def test_value(expression: Expression,
               expression_or_real: Union[Real, Expression]) -> None:
    result = expression % expression_or_real

    assert (result == 0 and (expression / expression_or_real
                             == expression // expression_or_real)
            or (result > 0) is (expression_or_real > 0))
    assert abs(result) < abs(expression_or_real)


@given(strategies.finite_expressions)
def test_modulo_one(expression: Expression) -> None:
    result = expression % 1

    assert result == expression - math.floor(expression)


@given(strategies.finite_expressions,
       strategies.finite_non_zero_reals_or_expressions)
def test_connection_with_floordiv(expression: Expression,
                                  expression_or_real: Union[Real, Expression]
                                  ) -> None:
    result = expression % expression_or_real

    assert (result + (expression // expression_or_real) * expression_or_real
            == expression)
