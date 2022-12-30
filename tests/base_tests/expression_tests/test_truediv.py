from numbers import Real
from typing import Union

from hypothesis import given

from symba.base import Expression
from tests.utils import equivalence
from . import strategies


@given(strategies.expressions, strategies.non_zero_finite_reals_or_expressions)
def test_basic(expression: Expression,
               real_or_expression: Union[Real, Expression]) -> None:
    result = expression / real_or_expression

    assert isinstance(result, Expression)


@given(strategies.finite_non_zero_expressions)
def test_self_inverse(expression: Expression) -> None:
    assert expression / expression == 1


@given(strategies.finite_non_zero_expressions,
       strategies.finite_non_zero_expressions)
def test_commutative_case(first: Expression, second: Expression) -> None:
    assert equivalence(first / second == second / first,
                       abs(first) == abs(second))


@given(strategies.expressions, strategies.unary_reals_or_expressions)
def test_right_neutral_element(
        expression: Expression,
        real_or_expression: Union[Real, Expression]
) -> None:
    assert expression / real_or_expression == expression


@given(strategies.finite_expressions, strategies.finite_expressions,
       strategies.non_zero_reals_or_expressions)
def test_add_dividend(first: Expression,
                      second: Expression,
                      real_or_expression: Expression) -> None:
    result = (first + second) / real_or_expression

    assert result == ((first / real_or_expression)
                      + (second / real_or_expression))


@given(strategies.finite_expressions, strategies.finite_expressions,
       strategies.non_zero_reals_or_expressions)
def test_sub_dividend(first: Expression,
                      second: Expression,
                      real_or_expression: Expression) -> None:
    result = (first - second) / real_or_expression

    assert result == ((first / real_or_expression)
                      - (second / real_or_expression))


@given(strategies.finite_expressions,
       strategies.non_zero_reals_or_expressions,
       strategies.non_zero_reals_or_expressions)
def test_mul_divisor(
        expression: Expression,
        first_real_or_expression: Union[Real, Expression],
        second_real_or_expression: Union[Real, Expression]
) -> None:
    result = expression / (first_real_or_expression
                           * second_real_or_expression)

    assert result == ((expression / first_real_or_expression)
                      / second_real_or_expression)
