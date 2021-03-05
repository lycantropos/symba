from numbers import Real
from typing import Union

from hypothesis import given

from symba.base import Expression
from . import strategies


@given(strategies.expressions, strategies.reals_or_expressions)
def test_basic(expression: Expression,
               real_or_expression: Union[Real, Expression]) -> None:
    result = expression + real_or_expression

    assert isinstance(result, Expression)


@given(strategies.expressions, strategies.reals_or_expressions)
def test_commutativity(expression: Expression,
                       real_or_expression: Union[Real, Expression]) -> None:
    result = expression + real_or_expression

    assert result == real_or_expression + expression


@given(strategies.expressions, strategies.zero_reals_or_expressions)
def test_right_neutral_element(expression: Expression,
                               real_or_expression: Union[Real, Expression]
                               ) -> None:
    result = expression + real_or_expression

    assert result == expression


@given(strategies.expressions, strategies.reals_or_expressions,
       strategies.reals_or_expressions)
def test_associativity(expression: Expression,
                       first_real_or_expression: Union[Real, Expression],
                       second_real_or_expression: Union[Real, Expression]
                       ) -> None:
    result = expression + first_real_or_expression

    assert (result + second_real_or_expression
            == expression + (first_real_or_expression
                             + second_real_or_expression))
