from fractions import Fraction
from numbers import Real
from typing import (Optional,
                    Union)

from reprit.base import generate_repr

from .abcs import Expression
from .hints import SquareRooter
from .utils import (sqrt_ceil,
                    sqrt_floor)


class Constant(Expression):
    __slots__ = 'value',

    def __init__(self, value: Real = 0) -> None:
        assert isinstance(value, Real)
        self.value = Fraction(value)

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

    def __eq__(self, other: Union[Real, 'Constant']) -> bool:
        return (self.value == other
                if isinstance(other, Real)
                else (self.value == other.value
                      if isinstance(other, Constant)
                      else NotImplemented))

    def __ge__(self, other: Union[Real, 'Constant']) -> bool:
        return (self.value >= other
                if isinstance(other, (Real, Constant))
                else NotImplemented)

    def __gt__(self, other: Union[Real, 'Constant']) -> bool:
        return (self.value > other
                if isinstance(other, (Real, Constant))
                else NotImplemented)

    def __hash__(self) -> int:
        return hash(self.value)

    def __le__(self, other: Union[Real, 'Constant']) -> bool:
        return (self.value <= other
                if isinstance(other, (Real, Constant))
                else NotImplemented)

    def __lt__(self, other: Union[Real, 'Constant']) -> bool:
        return (self.value < other
                if isinstance(other, (Real, Constant))
                else NotImplemented)

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

    def __rsub__(self, other: Real) -> 'Constant':
        return other + (-self)

    def __rtruediv__(self, other: Real) -> 'Constant':
        return (Constant(other / self.value)
                if isinstance(other, Real)
                else NotImplemented)

    def __str__(self) -> str:
        return str(self.value)

    def __sub__(self, other: Union[Real, 'Constant']) -> 'Constant':
        return self + (-other)

    def __truediv__(self, other: Union[Real, 'Constant']) -> 'Constant':
        return (Constant(self.value / other)
                if isinstance(other, Real)
                else (Constant(self.value / other.value)
                      if isinstance(other, Constant)
                      else NotImplemented))

    def evaluate(self, square_rooter: Optional[SquareRooter] = None) -> Real:
        return self.value


Zero, One = Constant(0), Constant(1)


def constant_sqrt_ceil(value: Constant) -> Constant:
    fraction = value.value
    return Constant(Fraction(sqrt_ceil(fraction.numerator),
                             sqrt_floor(fraction.denominator)))


def constant_sqrt_floor(value: Constant) -> Constant:
    fraction = value.value
    return Constant(Fraction(sqrt_floor(fraction.numerator),
                             sqrt_ceil(fraction.denominator)))
