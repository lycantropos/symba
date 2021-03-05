from hypothesis import given

from symba.base import (get_sqrt_evaluator,
                        set_sqrt_evaluator)
from symba.hints import SqrtEvaluator
from . import strategies


@given(strategies.sqrt_evaluators)
def test_properties(sqrt_evaluator: SqrtEvaluator) -> None:
    set_sqrt_evaluator(sqrt_evaluator)

    assert get_sqrt_evaluator() is sqrt_evaluator
