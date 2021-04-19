from numbers import Real as _Real
from typing import Union as _Union

from .core import context as _context
from .core.expression import Expression
from .core.constant import (One as _One,
                            to_expression as _to_expression)
from .core.term import Term as _Term
from .hints import SqrtEvaluator as _SqrtEvaluator


def sqrt(argument: _Union[_Real, Expression]) -> Expression:
    """
    Returns square root of the argument:
        exact if it is a perfect square, symbolic instead.

    >>> sqrt(0) == 0
    True
    >>> sqrt(1) == 1
    True
    >>> square_root_of_two = sqrt(2)
    >>> square_root_of_two ** 2 == 2
    True
    >>> 1 < square_root_of_two < 2
    True
    """
    if argument < 0:
        raise ValueError('Argument should be non-negative.')
    expression = _to_expression(argument)
    return (_Term.from_components(_One, expression)
            if expression.is_finite
            else expression)


Expression = Expression


def get_sqrt_evaluator() -> _SqrtEvaluator:
    """
    Returns current square root evaluator.
    """
    return _context.sqrt_evaluator.get()


def set_sqrt_evaluator(evaluator: _SqrtEvaluator) -> None:
    """
    Sets square root evaluator.
    """
    _context.sqrt_evaluator.set(evaluator)
