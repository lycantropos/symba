from numbers import Real

import pytest
from hypothesis import given

from symba.base import Expression
from . import strategies


@given(strategies.reals, strategies.non_zero_finite_expressions)
def test_basic(real: Real, expression: Expression) -> None:
    result = real / expression

    assert isinstance(result, Expression)


@given(strategies.reals_or_expressions, strategies.unary_expressions)
def test_right_neutral_element(real: Real, expression: Expression) -> None:
    assert real / expression == real


@given(strategies.finite_reals_or_expressions,
       strategies.finite_reals_or_expressions,
       strategies.non_zero_expressions)
def test_add_dividend(first_real: Real,
                      second_real: Real,
                      expression: Expression) -> None:
    assert ((first_real + second_real) / expression
            == (first_real / expression) + (second_real / expression))


@given(strategies.finite_reals_or_expressions,
       strategies.finite_reals_or_expressions,
       strategies.non_zero_expressions)
def test_sub_dividend(first_real: Real,
                      second_real: Real,
                      expression: Expression) -> None:
    assert ((first_real - second_real) / expression
            == (first_real / expression) - (second_real / expression))


@given(strategies.finite_reals, strategies.non_zero_expressions,
       strategies.non_zero_expressions)
def test_mul_divisor(real: Real,
                     first: Expression,
                     second: Expression) -> None:
    assert real / (first * second) == (real / first) / second


@given(strategies.reals, strategies.zero_expressions)
def test_division_by_zero(real: Real, expression: Expression) -> None:
    with pytest.raises(ZeroDivisionError):
        real / expression


@given(strategies.infinite_reals, strategies.infinite_expressions)
def test_infinity_by_infinity(real: Real, expression: Expression) -> None:
    with pytest.raises(ArithmeticError):
        real / expression
