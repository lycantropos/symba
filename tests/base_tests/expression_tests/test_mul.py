from numbers import Real
from typing import (Tuple,
                    Union)

from hypothesis import given

from symba.base import Expression
from . import strategies


@given(strategies.expressions, strategies.reals_or_expressions)
def test_basic(expression: Expression,
               real_or_expression: Union[Real, Expression]) -> None:
    result = expression * real_or_expression

    assert isinstance(result, Expression)


@given(strategies.definitely_multipliable_expressions_pairs)
def test_commutativity(expressions_pair: Tuple[Expression, Expression]
                       ) -> None:
    first_expression, second_expression = expressions_pair

    result = first_expression * second_expression

    assert result == second_expression * first_expression


@given(strategies.unary_expressions, strategies.definite_reals_or_expressions)
def test_left_neutral_element(expression: Expression,
                              real_or_expression: Union[Real, Expression]
                              ) -> None:
    result = expression * real_or_expression

    assert result == real_or_expression


@given(strategies.definite_expressions, strategies.unary_reals_or_expressions)
def test_right_neutral_element(expression: Expression,
                               real_or_expression: Union[Real, Expression]
                               ) -> None:
    result = expression * real_or_expression

    assert result == expression


@given(strategies.definitely_multipliable_expressions_triplets)
def test_associativity(expressions_triplet
                       : Tuple[Expression, Expression, Expression]) -> None:
    first_expression, second_expression, third_expression = expressions_triplet

    assert ((first_expression * second_expression) * third_expression
            == first_expression * (second_expression * third_expression))
