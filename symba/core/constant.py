import math
from abc import abstractmethod
from fractions import Fraction
from numbers import (Rational,
                     Real)
from typing import (Any,
                    Optional,
                    Tuple,
                    Union)

from reprit.base import generate_repr

from .expression import Expression
from .hints import SqrtEvaluator
from .utils import (digits_count,
                    identity,
                    positiveness_to_sign,
                    perfect_sqrt,
                    square)


class Constant(Expression):
    @property
    def degree(self) -> int:
        return 0

    @property
    @abstractmethod
    def value(self) -> Real:
        """Returns value of the constant."""

    def evaluate(self, sqrt_evaluator: Optional[SqrtEvaluator] = None) -> Real:
        return self.value

    def is_positive(self) -> bool:
        return self.value > 0

    def lower_bound(self) -> Real:
        return self.value

    upper_bound = lower_bound

    def __eq__(self, other: Any) -> Any:
        return (self.value == other
                if isinstance(other, Real)
                else (isinstance(other, Constant)
                      and self.value == other.value
                      if isinstance(other, Expression)
                      else NotImplemented))

    def __hash__(self) -> int:
        return hash(self.value)

    def __str__(self) -> str:
        return str(self.value)


class Finite(Constant):
    """Represents rational number."""
    is_finite = True

    __slots__ = '_value',

    def __init__(self, value: Real = 0) -> None:
        self._value = Fraction(value)

    @property
    def value(self) -> Rational:
        return self._value

    def evaluate(self, sqrt_evaluator: Optional[SqrtEvaluator] = None) -> Real:
        return self.value

    def extract_common_denominator(self) -> Tuple[int, 'Finite']:
        return self.value.denominator, Finite(self.value.numerator)

    def extract_common_numerator(self) -> Tuple[int, 'Finite']:
        return self.value.numerator, One / self.value.denominator

    def inverse(self) -> 'Finite':
        return Finite(Fraction(self.value.denominator, self.value.numerator))

    def is_positive(self) -> bool:
        return self.value > 0

    def perfect_sqrt(self) -> Expression:
        return Finite(Fraction(perfect_sqrt(self.value.numerator),
                               perfect_sqrt(self.value.denominator)))

    def significant_digits_count(self) -> int:
        return digits_count(self._value.limit_denominator(1).numerator)

    def square(self) -> 'Finite':
        return Finite(square(self.value))

    def __add__(self, other: Union[Real, 'Finite']) -> 'Finite':
        other = to_expression(other)
        return ((Finite(self.value + other.value)
                 if isinstance(other, Finite)
                 else other.__radd__(self))
                if isinstance(other, Expression)
                else NotImplemented)

    def __bool__(self) -> bool:
        return bool(self.value)

    def __mul__(self, other: Union[Real, 'Finite']) -> 'Finite':
        other = to_expression(other)
        return ((Finite(self.value * other.value)
                 if isinstance(other, Finite)
                 else other.__rmul__(self))
                if isinstance(other, Expression)
                else NotImplemented)

    def __neg__(self) -> 'Finite':
        return Finite(-self.value)

    def __radd__(self, other: Union[Real, 'Finite']) -> 'Finite':
        return (to_expression(other) + self
                if isinstance(other, Real)
                else NotImplemented)

    __repr__ = generate_repr(__init__)

    def __rmul__(self, other: Union[Real, 'Finite']) -> 'Finite':
        return (to_expression(other) * self
                if isinstance(other, Real)
                else NotImplemented)


Zero, One = Finite(0), Finite(1)


class Infinite(Constant):
    is_finite = False

    @property
    def degree(self) -> int:
        return 0

    @property
    def value(self) -> Real:
        return positiveness_to_sign(self.is_positive()) * math.inf

    __slots__ = '_is_positive',

    def __init__(self, is_positive: bool) -> None:
        self._is_positive = is_positive

    def evaluate(self, sqrt_evaluator: Optional[SqrtEvaluator] = None) -> Real:
        return self.value

    def extract_common_denominator(self) -> Tuple[int, 'Expression']:
        return 1, self

    def extract_common_numerator(self) -> Tuple[int, 'Expression']:
        return 1, self

    def inverse(self) -> 'Expression':
        return Zero

    def is_positive(self) -> bool:
        return self._is_positive

    perfect_sqrt = identity

    def significant_digits_count(self) -> int:
        return 0

    def square(self) -> 'Expression':
        return Infinity

    def __add__(self, other: Union[Real, 'Expression']) -> Constant:
        other = to_expression(other)
        return ((self
                 if (other.is_finite
                     or (other is not NaN
                         and self.is_positive() is other.is_positive()))
                 else NaN)
                if isinstance(other, Expression)
                else NotImplemented)

    def __ge__(self, other: Union[Real, 'Expression']) -> bool:
        other = to_expression(other)
        return (other is not NaN and (self.is_positive() or self == other)
                if isinstance(other, (Real, Expression))
                else NotImplemented)

    def __gt__(self, other: Union[Real, 'Expression']) -> bool:
        other = to_expression(other)
        return (other is not NaN and self.is_positive() and self != other
                if isinstance(other, Expression)
                else NotImplemented)

    def __le__(self, other: Union[Real, 'Expression']) -> bool:
        other = to_expression(other)
        return (other is not NaN and (not self.is_positive() or self == other)
                if isinstance(other, Expression)
                else NotImplemented)

    def __lt__(self, other: Union[Real, 'Expression']) -> bool:
        other = to_expression(other)
        return (other is not NaN and not self.is_positive() and self != other
                if isinstance(other, Expression)
                else NotImplemented)

    def __mul__(self, other: Union[Real, 'Expression']) -> Constant:
        other = to_expression(other)
        return (((Infinity
                  if self.is_positive() is other.is_positive()
                  else -Infinity)
                 if other and other is not NaN
                 else NaN)
                if isinstance(other, Expression)
                else NotImplemented)

    def __neg__(self) -> 'Expression':
        return Infinite(not self.is_positive())

    __radd__ = __add__
    __repr__ = generate_repr(__init__)
    __rmul__ = __mul__


Infinity = Infinite(True)


class _NaN(Constant):
    is_finite = False
    value = math.nan
    _instance = None

    def __new__(cls) -> '_NaN':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    __slots__ = ()

    def extract_common_denominator(self) -> Tuple[int, 'Expression']:
        return 1, self

    def extract_common_numerator(self) -> Tuple[int, 'Expression']:
        return 1, self

    def inverse(self) -> 'Expression':
        return self

    def is_positive(self) -> bool:
        return False

    perfect_sqrt = identity

    def significant_digits_count(self) -> int:
        return 0

    square = identity

    def __add__(self, other: Union[Real, 'Expression']) -> 'Expression':
        return self

    def __ge__(self, other: Union[Real, 'Expression']) -> bool:
        return (False
                if isinstance(other, (Real, Expression))
                else NotImplemented)

    def __gt__(self, other: Union[Real, 'Expression']) -> bool:
        return (False
                if isinstance(other, (Real, Expression))
                else NotImplemented)

    def __le__(self, other: Union[Real, 'Expression']) -> bool:
        return (False
                if isinstance(other, (Real, Expression))
                else NotImplemented)

    def __lt__(self, other: Union[Real, 'Expression']) -> bool:
        return (False
                if isinstance(other, (Real, Expression))
                else NotImplemented)

    def __mul__(self, other: Union[Real, 'Expression']) -> 'Expression':
        return self

    __neg__ = identity

    def __radd__(self, other: Union[Real, 'Expression']) -> 'Expression':
        return self

    def __repr__(self) -> str:
        return 'NaN'

    def __rmul__(self, other: Union[Real, 'Expression']) -> 'Expression':
        return self


NaN = _NaN()


def to_expression(other: Union[Real, Expression]) -> Expression:
    return ((Finite(other)
             if isinstance(other, Rational) or math.isfinite(other)
             else (Infinite(other > 0)
                   if math.isinf(other)
                   else NaN))
            if isinstance(other, Real)
            else other)
