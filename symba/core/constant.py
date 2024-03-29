from __future__ import annotations

import math
from abc import abstractmethod
from numbers import (Rational,
                     Real)
from typing import (Any,
                    NoReturn,
                    Tuple,
                    TypeVar,
                    Union,
                    overload)

from cfractions import Fraction
from reprit.base import generate_repr

from .expression import Expression
from .hints import (RawConstant,
                    RawFinite,
                    RawUnbound)
from .utils import (digits_count,
                    identity,
                    perfect_sqrt,
                    positiveness_to_sign)

RAW_ZERO = Fraction(0)
RAW_ONE = Fraction(1)


class Constant(Expression):
    @property
    def degree(self) -> int:
        return 0

    @property
    @abstractmethod
    def raw(self) -> RawConstant:
        """Returns value of the constant."""

    def lower_bound(self) -> RawConstant:
        return self.raw

    upper_bound = lower_bound

    def __eq__(self, other: Any) -> Any:
        return (isinstance(other, Constant) and self.raw == other.raw
                if isinstance(other, Expression)
                else (self.raw == other
                      if isinstance(other, (Rational, Real))
                      else NotImplemented))

    def __hash__(self) -> int:
        return hash(self.raw)

    def __str__(self) -> str:
        return str(self.raw)


_Expression = TypeVar('_Expression',
                      bound=Expression)


class Zero(Constant):
    """Represents zero."""

    @property
    def raw(self) -> Fraction:
        return RAW_ZERO

    def extract_common_denominator(self) -> Tuple[int, Zero]:
        return 1, self

    def extract_common_numerator(self) -> Tuple[int, FiniteNonZero]:
        return 0, ONE

    def inverse(self) -> NoReturn:
        raise ZeroDivisionError()

    def is_positive(self) -> bool:
        return False

    def perfect_sqrt(self) -> Zero:
        return self

    def significant_digits_count(self) -> int:
        return 1

    def square(self) -> Zero:
        return self

    def __new__(cls) -> Zero:
        return super().__new__(cls)

    @overload
    def __add__(self, other: RawFinite) -> Finite:
        ...

    @overload
    def __add__(self, other: RawUnbound) -> Union[Finite, Infinite]:
        ...

    @overload
    def __add__(self, other: Zero) -> Zero:
        ...

    @overload
    def __add__(self, other: _Expression) -> _Expression:
        ...

    @overload
    def __add__(self, other: Any) -> Any:
        ...

    def __add__(self, other: Any) -> Any:
        other = try_to_constant(other)
        return (other
                if isinstance(other, Expression)
                else NotImplemented)

    def __bool__(self) -> bool:
        return False

    @overload
    def __mul__(self, other: Union[RawConstant, Zero]) -> Zero:
        ...

    @overload
    def __mul__(self, other: Any) -> Any:
        ...

    def __mul__(self, other: Any) -> Any:
        other = try_to_constant(other)
        return (self
                if isinstance(other, Zero)
                else (other * self
                      if isinstance(other, Expression)
                      else NotImplemented))

    def __neg__(self) -> Zero:
        return self

    @overload
    def __radd__(self, other: RawFinite) -> Finite:
        ...

    @overload
    def __radd__(self, other: RawUnbound) -> Union[Finite, Infinite]:
        ...

    @overload
    def __radd__(self, other: _Expression) -> _Expression:
        ...

    @overload
    def __radd__(self, other: Any) -> Any:
        ...

    def __radd__(self, other: Any) -> Any:
        other = try_to_constant(other)
        return (other
                if isinstance(other, Expression)
                else NotImplemented)

    __repr__ = generate_repr(__new__)

    @overload
    def __rmul__(self, other: Union[RawConstant, Zero]) -> Zero:
        ...

    @overload
    def __rmul__(self, other: Any) -> Any:
        ...

    def __rmul__(self, other: Any) -> Any:
        other = try_to_constant(other)
        return (other * self
                if isinstance(other, Expression)
                else NotImplemented)


class FiniteNonZero(Constant):
    """Represents non-zero rational number."""

    @property
    def raw(self) -> Fraction:
        return self._raw

    def extract_common_denominator(self) -> Tuple[int, FiniteNonZero]:
        return self.raw.denominator, FiniteNonZero(self.raw.numerator)

    def extract_common_numerator(self) -> Tuple[int, FiniteNonZero]:
        return self.raw.numerator, ONE / self.raw.denominator

    def inverse(self) -> FiniteNonZero:
        return FiniteNonZero(Fraction(self.raw.denominator,
                                      self.raw.numerator))

    def is_positive(self) -> bool:
        return self.raw > 0

    def perfect_sqrt(self) -> FiniteNonZero:
        return FiniteNonZero(Fraction(perfect_sqrt(self.raw.numerator),
                                      perfect_sqrt(self.raw.denominator)))

    def significant_digits_count(self) -> int:
        return digits_count(self._raw.limit_denominator(1).numerator)

    def square(self) -> FiniteNonZero:
        return FiniteNonZero(self.raw * self.raw)

    _raw: Fraction

    __slots__ = '_raw',

    def __init__(self, raw: RawConstant) -> None:
        assert raw and (isinstance(raw, Rational) or math.isfinite(raw)), raw
        self._raw = Fraction(raw)

    @overload
    def __add__(self, other: RawConstant) -> Union[FiniteNonZero, Infinite]:
        ...

    @overload
    def __add__(self, other: FiniteNonZero) -> FiniteNonZero:
        ...

    @overload
    def __add__(self, other: Zero) -> FiniteNonZero:
        ...

    @overload
    def __add__(self, other: Any) -> Any:
        ...

    def __add__(self, other: Any) -> Any:
        other = try_to_constant(other)
        return (to_constant(self.raw + other.raw)
                if isinstance(other, FiniteNonZero)
                else (other + self
                      if isinstance(other, Expression)
                      else NotImplemented))

    def __bool__(self) -> bool:
        return bool(self.raw)

    def __hash__(self) -> int:
        return hash(self.raw)

    @overload
    def __mul__(self, other: FiniteNonZero) -> FiniteNonZero:
        ...

    @overload
    def __mul__(self, other: RawFinite) -> Union[FiniteNonZero, Zero]:
        ...

    @overload
    def __mul__(self, other: RawUnbound) -> Union[FiniteNonZero, Infinite]:
        ...

    @overload
    def __mul__(self, other: Zero) -> Zero:
        ...

    @overload
    def __mul__(self, other: Any) -> Any:
        ...

    def __mul__(self, other: Any) -> Any:
        other = try_to_constant(other)
        return (FiniteNonZero(self.raw * other.raw)
                if isinstance(other, FiniteNonZero)
                else (other
                      if isinstance(other, Zero)
                      else (other * self
                            if isinstance(other, Expression)
                            else NotImplemented)))

    def __neg__(self) -> FiniteNonZero:
        return FiniteNonZero(-self.raw)

    @overload
    def __radd__(self, other: RawConstant) -> Union[FiniteNonZero, Infinite]:
        ...

    @overload
    def __radd__(self, other: Any) -> Any:
        ...

    def __radd__(self, other: Any) -> Any:
        other = try_to_constant(other)
        return (other + self
                if isinstance(other, Expression)
                else NotImplemented)

    __repr__ = generate_repr(__init__)

    @overload
    def __rmul__(self, other: RawConstant) -> FiniteNonZero:
        ...

    @overload
    def __rmul__(self, other: Zero) -> Zero:
        ...

    @overload
    def __rmul__(self, other: Any) -> Any:
        ...

    def __rmul__(self, other: Any) -> Any:
        other = try_to_constant(other)
        return (other
                if isinstance(other, Zero)
                else (other * self
                      if isinstance(other, Expression)
                      else NotImplemented))


Finite = Union[FiniteNonZero, Zero]

ZERO, ONE = Zero(), FiniteNonZero(1)


class Infinite(Constant):
    @property
    def raw(self) -> float:
        return positiveness_to_sign(self.is_positive()) * math.inf

    def extract_common_denominator(self) -> Tuple[int, Expression]:
        return 1, self

    def extract_common_numerator(self) -> Tuple[int, Expression]:
        return 1, self

    def inverse(self) -> Expression:
        return ZERO

    def is_positive(self) -> bool:
        return self._is_positive

    perfect_sqrt = identity

    def significant_digits_count(self) -> int:
        return 0

    def square(self) -> Expression:
        return Infinity

    __slots__ = '_is_positive',

    def __init__(self, is_positive: bool) -> None:
        self._is_positive = is_positive

    def __hash__(self) -> int:
        return hash(self.raw)

    @overload
    def __add__(self, other: Union[RawConstant, Expression]) -> Infinite:
        ...

    @overload
    def __add__(self, other: Any) -> Any:
        ...

    def __add__(self, other: Any) -> Any:
        other = try_to_constant(other)
        return (self._add_expression(other)
                if isinstance(other, Expression)
                else NotImplemented)

    @overload
    def __ge__(self, other: Union[RawConstant, Expression]) -> bool:
        ...

    @overload
    def __ge__(self, other: Any) -> Any:
        ...

    def __ge__(self, other: Any) -> Any:
        other = try_to_constant(other)
        return ((self.is_positive() or self == other)
                if isinstance(other, Expression)
                else NotImplemented)

    @overload
    def __gt__(self, other: Union[RawConstant, Expression]) -> bool:
        ...

    @overload
    def __gt__(self, other: Any) -> Any:
        ...

    def __gt__(self, other: Any) -> Any:
        other = try_to_constant(other)
        return ((self.is_positive() and self != other)
                if isinstance(other, Expression)
                else NotImplemented)

    def __le__(self,
               other: Union[RawConstant, Expression]) -> bool:
        other = try_to_constant(other)
        return ((not self.is_positive() or self == other)
                if isinstance(other, Expression)
                else NotImplemented)

    @overload
    def __lt__(self, other: Union[RawConstant, Expression]) -> bool:
        ...

    @overload
    def __lt__(self, other: Any) -> Any:
        ...

    def __lt__(self, other: Any) -> Any:
        other = try_to_constant(other)
        return ((not self.is_positive() and self != other)
                if isinstance(other, Expression)
                else NotImplemented)

    @overload
    def __mul__(self, other: Zero) -> NoReturn:
        ...

    @overload
    def __mul__(self, other: Union[RawConstant, Expression]) -> Infinite:
        ...

    @overload
    def __mul__(self, other: Any) -> Any:
        ...

    def __mul__(self, other: Any) -> Any:
        other = try_to_constant(other)
        return (self._mul_by_expression(other)
                if isinstance(other, Expression)
                else NotImplemented)

    def __neg__(self) -> Infinite:
        return Infinite(not self.is_positive())

    @overload
    def __radd__(self, other: Union[RawConstant, Expression]) -> Infinite:
        ...

    @overload
    def __radd__(self, other: Any) -> Any:
        ...

    def __radd__(self, other: Any) -> Any:
        other = try_to_constant(other)
        return (self._add_expression(other)
                if isinstance(other, Expression)
                else NotImplemented)

    __repr__ = generate_repr(__init__)

    @overload
    def __rmul__(self, other: Zero) -> NoReturn:
        ...

    @overload
    def __rmul__(self, other: Union[RawConstant, Expression]) -> Infinite:
        ...

    @overload
    def __rmul__(self, other: Any) -> Any:
        ...

    def __rmul__(self, other: Any) -> Any:
        other = try_to_constant(other)
        return (self._mul_by_expression(other)
                if isinstance(other, Expression)
                else NotImplemented)

    def _add_expression(self, other: Expression) -> Infinite:
        if (isinstance(other, Infinite)
                and self.is_positive() is not other.is_positive()):
            raise ArithmeticError('Sum of infinities with different signs '
                                  'is undefined.')
        return self

    def _mul_by_expression(self, other: Expression) -> Infinite:
        if not other:
            raise ArithmeticError('Multiplication of infinity by zero '
                                  'is undefined.')
        return (Infinity
                if self.is_positive() is other.is_positive()
                else -Infinity)


Infinity = Infinite(True)


@overload
def to_constant(_value: RawFinite) -> Union[FiniteNonZero, Zero]:
    ...


@overload
def to_constant(_value: RawUnbound) -> Union[FiniteNonZero, Infinite, Zero]:
    ...


def to_constant(_value: RawConstant) -> Union[FiniteNonZero, Infinite, Zero]:
    if not isinstance(_value, Rational) and math.isnan(_value):
        raise ValueError('NaN values are not supported.')
    return ((FiniteNonZero(_value) if _value else ZERO)
            if isinstance(_value, Rational) or math.isfinite(_value)
            else Infinite(_value > 0))


@overload
def try_to_constant(_value: RawFinite) -> Union[FiniteNonZero, Zero]:
    ...


@overload
def try_to_constant(
        _value: RawUnbound
) -> Union[FiniteNonZero, Infinite, Zero]:
    ...


@overload
def try_to_constant(_value: Any) -> Any:
    ...


def try_to_constant(_value: Any) -> Any:
    if not isinstance(_value, Rational):
        if isinstance(_value, Real):
            if math.isnan(_value):
                raise ValueError('NaN values are not supported.')
            elif math.isinf(_value):
                return Infinite(float(_value) > 0)
        try:
            numerator, denominator = _value.as_integer_ratio()
        except Exception:
            return _value
        else:
            _value = Fraction(numerator, denominator)
    return FiniteNonZero(_value) if _value else ZERO
