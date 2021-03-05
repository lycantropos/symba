from numbers import Real
from typing import Union

from hypothesis import given

from symba.base import Expression
from tests.utils import equivalence
from . import strategies


@given(strategies.reals_or_expressions, strategies.expressions)
def test_basic(real_or_expression: Union[Real, Expression],
               expression: Expression) -> None:
    result = real_or_expression - expression

    assert isinstance(result, Expression)


@given(strategies.reals_or_expressions, strategies.expressions)
def test_commutative_case(real_or_expression: Union[Real, Expression],
                          expression: Expression) -> None:
    result = real_or_expression - expression

    assert equivalence(result == expression - real_or_expression,
                       expression == real_or_expression == 0)


@given(strategies.reals_or_expressions, strategies.zero_expressions)
def test_right_neutral_element(real_or_expression: Union[Real, Expression],
                               expression: Expression) -> None:
    result = real_or_expression - expression

    assert result == real_or_expression


@given(strategies.reals_or_expressions, strategies.expressions,
       strategies.expressions)
def test_add_subtrahend(real_or_expression: Union[Real, Expression],
                        first_expression: Expression,
                        second_expression: Expression) -> None:
    result = real_or_expression - (first_expression + second_expression)

    assert result == real_or_expression - first_expression - second_expression


@given(strategies.reals_or_expressions, strategies.expressions)
def test_connection_with_sub(real_or_expression: Union[Real, Expression],
                             expression: Expression) -> None:
    result = real_or_expression - expression

    assert result == -(expression - real_or_expression)
