from numbers import Real as _Real
from typing import Union as _Union

from .core.abcs import Expression
from .core.constant import (Constant as _Constant,
                            One as _One)
from .core.term import Term as _Term

Expression = Expression


def sqrt(argument: _Union[_Real, Expression]) -> Expression:
    if argument < 0:
        raise ValueError('Argument should be non-negative.')
    return _Term.from_components(_One, (_Constant(argument)
                                        if isinstance(argument, _Real)
                                        else argument))
