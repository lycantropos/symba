from numbers import Real
from typing import Tuple, Union

from hypothesis import given

from symba.base import Expression
from tests.utils import equivalence
from . import strategies


@given(strategies.expressions, strategies.reals_or_expressions)
def test_basic(expression: Expression,
               real_or_expression: Union[Real, Expression]) -> None:
    result = expression - real_or_expression

    assert isinstance(result, Expression)


@given(strategies.finite_expressions)
def test_self_inverse(expression: Expression) -> None:
    result = expression - expression

    assert result == 0


@given(strategies.definitely_subtractable_expressions_pairs)
def test_commutative_case(expressions_pair: Tuple[Expression, Expression]
                          ) -> None:
    first_expression, second_expression = expressions_pair

    result = first_expression - second_expression

    assert equivalence(result == second_expression - first_expression,
                       first_expression == second_expression)


@given(strategies.definite_expressions, strategies.zero_reals_or_expressions)
def test_right_neutral_element(expression: Expression,
                               real_or_expression: Union[Real, Expression]
                               ) -> None:
    result = expression - real_or_expression

    assert result == expression


@given(strategies.finite_expressions, strategies.finite_reals_or_expressions,
       strategies.finite_reals_or_expressions)
def test_add_subtrahend(first_expression: Expression,
                        second_expression: Expression,
                        third_expression: Expression) -> None:
    result = first_expression - (second_expression + third_expression)

    assert result == (first_expression - second_expression - third_expression)
