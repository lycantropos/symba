from hypothesis import given

from symba.base import Expression
from tests.utils import pickle_round_trip
from . import strategies


@given(strategies.expressions)
def test_round_trip(expression: Expression) -> None:
    assert pickle_round_trip(expression) == expression
