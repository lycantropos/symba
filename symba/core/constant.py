import math
from fractions import Fraction
from numbers import (Rational,
                     Real)
from typing import (Any,
                    Optional,
                    Union)

from reprit.base import generate_repr

from .abcs import Expression
from .hints import SquareRooter


class Constant(Expression):
    __slots__ = '_value',

    def __init__(self, value: Real = 0) -> None:
        self._value = Fraction(value)

    @property
    def value(self) -> Rational:
        return self._value

    def evaluate(self, square_rooter: Optional[SquareRooter] = None) -> Real:
        return self.value

    def is_positive(self) -> bool:
        return self.value > 0

    def lower_bound(self) -> Rational:
        return self.value

    upper_bound = lower_bound

    def __abs__(self) -> 'Constant':
        return Constant(abs(self.value))

    def __add__(self, other: Union[Real, 'Constant']) -> 'Constant':
        return (Constant(self.value + other)
                if isinstance(other, Real)
                else (Constant(self.value + other.value)
                      if isinstance(other, Constant)
                      else NotImplemented))

    def __bool__(self) -> bool:
        return bool(self.value)

    def __ceil__(self) -> int:
        return math.ceil(self.value)

    def __eq__(self, other: Any) -> Any:
        return (self.value == other
                if isinstance(other, Real)
                else (self.value == other.value
                      if isinstance(other, Constant)
                      else NotImplemented))

    def __floor__(self) -> int:
        return math.floor(self.value)

    def __hash__(self) -> int:
        return hash(self.value)

    def __mul__(self, other: Union[Real, 'Constant']) -> 'Constant':
        return (Constant(self.value * other.value)
                if isinstance(other, Constant)
                else (Constant(self.value * other)
                      if isinstance(other, Real)
                      else NotImplemented))

    def __neg__(self) -> 'Constant':
        return Constant(-self.value)

    def __radd__(self, other: Real) -> 'Constant':
        return (Constant(other + self.value)
                if isinstance(other, Real)
                else NotImplemented)

    __repr__ = generate_repr(__init__)

    def __rmul__(self, other: Real) -> 'Constant':
        return (Constant(self.value * other)
                if isinstance(other, Real)
                else NotImplemented)

    def __rtruediv__(self, other: Real) -> 'Constant':
        return (Constant(other / self.value)
                if isinstance(other, Real)
                else NotImplemented)

    def __str__(self) -> str:
        return str(self.value)

    def __truediv__(self, other: Union[Real, 'Constant']) -> 'Constant':
        return (Constant(self.value / other)
                if isinstance(other, Real)
                else (Constant(self.value / other.value)
                      if isinstance(other, Constant)
                      else NotImplemented))


Zero, One = Constant(0), Constant(1)
