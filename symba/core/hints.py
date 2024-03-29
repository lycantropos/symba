import numbers
from typing import Union

RawFinite = Union[numbers.Rational, int]
RawUnbound = float
RawConstant = Union[RawUnbound, RawFinite]
