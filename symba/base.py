from typing import Union as _Union

from .core import expression as _expression
from .core.constant import (ONE as _ONE,
                            Infinite as _Infinite,
                            to_expression as _to_expression)
from .core.hints import RawConstant as _RawConstant
from .core.term import Term as _Term

Expression = _expression.Expression


def sqrt(argument: _Union[_RawConstant, Expression]) -> Expression:
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
    expression = (argument
                  if isinstance(argument, Expression)
                  else _to_expression(argument))
    return (expression
            if isinstance(expression, _Infinite)
            else _Term.from_components(_ONE, expression))
