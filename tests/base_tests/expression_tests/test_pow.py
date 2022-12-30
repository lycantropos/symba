from typing import Tuple

import pytest
from hypothesis import given

from symba.base import Expression
from . import strategies


@given(strategies.expressions_with_exponents)
def test_basic(expression_with_exponent: Tuple[Expression, int]) -> None:
    expression, exponent = expression_with_exponent

    result = expression ** exponent

    assert isinstance(result, Expression)


@given(strategies.expressions)
def test_identity(expression: Expression) -> None:
    result = expression ** 1

    assert result == expression


@given(strategies.expressions)
def test_zero_exponent(expression: Expression) -> None:
    result = expression ** 0

    assert result == 1


@given(strategies.non_zero_expressions,
       strategies.negative_exponents)
def test_negative_exponent(expression: Expression, exponent: int) -> None:
    result = expression ** exponent

    assert result == 1 / (expression ** -exponent)


@given(strategies.zero_expressions, strategies.positive_exponents)
def test_zero_base_with_positive_exponent(expression: Expression,
                                          exponent: int) -> None:
    result = expression ** exponent

    assert result == expression


@given(strategies.expressions, strategies.non_negative_exponents,
       strategies.non_negative_exponents)
def test_exponents_sum(expression: Expression,
                       first_exponent: int,
                       second_exponent: int) -> None:
    result = expression ** (first_exponent + second_exponent)

    assert result == ((expression ** first_exponent)
                      * (expression ** second_exponent))


@given(strategies.zero_expressions, strategies.negative_exponents)
def test_zero_base_with_negative_exponent(expression: Expression,
                                          exponent: int) -> None:
    with pytest.raises(ZeroDivisionError):
        expression ** exponent
