import math
from fractions import Fraction
from numbers import (Rational,
                     Real)
from typing import (Any,
                    Optional,
                    Tuple,
                    TypeVar,
                    Union,
                    overload)

from reprit.base import generate_repr

from .abcs import Expression
from .hints import SqrtEvaluator
from .utils import (digits_count,
                    sqrt_floor,
                    square)


class Constant(Expression):
    """Represents rational number."""

    __slots__ = '_value',

    def __init__(self, value: Real = 0) -> None:
        self._value = Fraction(value)

    @property
    def degree(self) -> int:
        return 0

    @property
    def value(self) -> Rational:
        return self._value

    def evaluate(self, sqrt_evaluator: Optional[SqrtEvaluator] = None) -> Real:
        return self.value

    def extract_common_denominator(self) -> Tuple[int, 'Constant']:
        return self.value.denominator, Constant(self.value.numerator)

    def extract_common_numerator(self) -> Tuple[int, 'Constant']:
        return self.value.numerator, One / self.value.denominator

    def inverse(self) -> 'Constant':
        return Constant(Fraction(self.value.denominator, self.value.numerator))

    def is_positive(self) -> bool:
        return self.value > 0

    def lower_bound(self) -> Rational:
        return self.value

    def perfect_sqrt(self) -> Expression:
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
        return Constant(result)

    def significant_digits_count(self) -> int:
        return digits_count(self._value.limit_denominator(1).numerator)

    def square(self) -> 'Constant':
        return Constant(square(self.value))

    upper_bound = lower_bound

    def __abs__(self) -> 'Constant':
        return Constant(abs(self.value))

    def __add__(self, other: Union[Real, 'Constant']) -> 'Constant':
        other = to_constant(other)
        return (Constant(self.value + other.value)
                if isinstance(other, Constant)
                else NotImplemented)

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
        other = to_constant(other)
        return (Constant(self.value * other.value)
                if isinstance(other, Constant)
                else NotImplemented)

    def __neg__(self) -> 'Constant':
        return Constant(-self.value)

    def __radd__(self, other: Union[Real, 'Constant']) -> 'Constant':
        return (Constant(other) + self
                if isinstance(other, Real)
                else NotImplemented)

    __repr__ = generate_repr(__init__)

    def __rmul__(self, other: Union[Real, 'Constant']) -> 'Constant':
        return (Constant(other) * self
                if isinstance(other, Real)
                else NotImplemented)

    def __str__(self) -> str:
        return str(self.value)


Zero, One = Constant(0), Constant(1)

_T = TypeVar('_T')


@overload
def to_constant(other: _T) -> _T:
    ...


@overload
def to_constant(other: Real) -> Constant:
    ...


def to_constant(other: Union[Real, Expression]) -> Expression:
    return Constant(other) if isinstance(other, Real) else other
