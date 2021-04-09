from numbers import Real
from typing import (Tuple,
                    Union)

from hypothesis import given

from symba.base import Expression
from . import strategies


@given(strategies.reals_or_expressions, strategies.expressions)
def test_basic(real_or_expression: Union[Real, Expression],
               expression: Expression) -> None:
    result = real_or_expression - expression

    assert isinstance(result, Expression)


@given(strategies.definite_reals_or_expressions, strategies.zero_expressions)
def test_right_neutral_element(real_or_expression: Union[Real, Expression],
                               expression: Expression) -> None:
    result = real_or_expression - expression

    assert result == real_or_expression


@given(strategies.finite_reals_or_expressions, strategies.finite_expressions,
       strategies.finite_expressions)
def test_add_subtrahend(real_or_expression: Union[Real, Expression],
                        first_expression: Expression,
                        second_expression: Expression) -> None:
    result = real_or_expression - (first_expression + second_expression)

    assert result == real_or_expression - first_expression - second_expression


@given(strategies
       .definitely_subtractable_expressions_with_reals_or_expressions)
def test_connection_with_sub(expression_with_real_or_expression
                             : Tuple[Expression, Union[Real, Expression]]
                             ) -> None:
    expression, real_or_expression = expression_with_real_or_expression

    result = real_or_expression - expression

    assert result == -(expression - real_or_expression)
