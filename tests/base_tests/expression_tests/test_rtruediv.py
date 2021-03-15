from numbers import Real

from hypothesis import given

from symba.base import Expression
from . import strategies


@given(strategies.reals, strategies.non_zero_expressions)
def test_basic(real: Real, expression: Expression) -> None:
    result = real / expression

    assert isinstance(result, Expression)


@given(strategies.reals_or_expressions, strategies.unary_expressions)
def test_right_neutral_element(real: Real, expression: Expression) -> None:
    result = real / expression

    assert result == real


@given(strategies.reals_or_expressions, strategies.reals_or_expressions,
       strategies.non_zero_expressions)
def test_add_dividend(first_real: Real,
                      second_real: Real,
                      expression: Expression) -> None:
    result = (first_real + second_real) / expression

    assert result == (first_real / expression) + (second_real / expression)


@given(strategies.reals_or_expressions, strategies.reals_or_expressions,
       strategies.non_zero_expressions)
def test_sub_dividend(first_real: Real,
                      second_real: Real,
                      expression: Expression) -> None:
    result = (first_real - second_real) / expression

    assert result == (first_real / expression) - (second_real / expression)


@given(strategies.reals, strategies.non_zero_expressions,
       strategies.non_zero_expressions)
def test_mul_divisor(real: Real,
                     first_expression: Expression,
                     second_expression: Expression) -> None:
    result = real / (first_expression * second_expression)

    assert result == (real / first_expression) / second_expression
