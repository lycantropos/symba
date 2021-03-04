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
from .utils import (integer_digits_count,
                    sqrt_floor,
                    square)


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

    def perfect_scale_sqrt(self) -> Rational:
        result = Fraction(1)
        argument_value = self.value
        argument_numerator = argument_value.numerator
        argument_numerator_sqrt_floor = sqrt_floor(argument_numerator)
        if square(argument_numerator_sqrt_floor) == argument_numerator:
            result *= argument_numerator_sqrt_floor
        argument_denominator = argument_value.denominator
        argument_denominator_sqrt_floor = sqrt_floor(argument_denominator)
        if square(argument_denominator_sqrt_floor) == argument_denominator:
            result /= argument_denominator_sqrt_floor
        elif argument_denominator != 1:
            result /= argument_denominator
        return result

    def significant_digits_count(self) -> int:
        return integer_digits_count(self._value.limit_denominator(1).numerator)

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
                      else (False
                            if isinstance(other, Expression)
                            else NotImplemented)))

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

    def __radd__(self, other: Union[Real, 'Constant']) -> 'Constant':
        return (Constant(other + self.value)
                if isinstance(other, Real)
                else NotImplemented)

    __repr__ = generate_repr(__init__)

    def __rmul__(self, other: Union[Real, 'Constant']) -> 'Constant':
        return (Constant(self.value * other)
                if isinstance(other, Real)
                else NotImplemented)

    def __rtruediv__(self, other: Union[Real, 'Constant']) -> 'Constant':
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
