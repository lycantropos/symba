from __future__ import annotations

import math
from abc import (ABC,
                 abstractmethod)
from numbers import Rational
from typing import (Any,
                    Optional,
                    Tuple,
                    TypeVar,
                    Union,
                    cast,
                    overload)

from cfractions import Fraction

from .hints import (RawConstant,
                    RawFinite,
                    RawUnbound)
from .utils import BASE

_Self = TypeVar('_Self',
                bound='Expression')


class Expression(ABC):
    __slots__ = ()

    @property
    @abstractmethod
    def degree(self) -> int:
        """Returns degree of the expression."""

    @abstractmethod
    def extract_common_denominator(self) -> Tuple[int, Expression]:
        """
        Returns a pair of the common denominator of the expression
        and the rest of the expression.
        """

    @abstractmethod
    def extract_common_numerator(self) -> Tuple[int, Expression]:
        """
        Returns a pair of the common numerator of the expression
        and the rest of the expression.
        """

    @abstractmethod
    def inverse(self) -> Expression:
        """Returns the expression inverted."""

    @abstractmethod
    def is_positive(self) -> bool:
        """Checks if the expression is positive."""

    @abstractmethod
    def lower_bound(self) -> RawConstant:
        """Returns lower bound of the expression."""

    @abstractmethod
    def perfect_sqrt(self) -> Expression:
        """Returns perfect square root part of the expression."""

    @abstractmethod
    def significant_digits_count(self) -> int:
        """Returns significant digits count of the expression."""

    @abstractmethod
    def square(self) -> Expression:
        """Returns the expression squared."""

    @abstractmethod
    def upper_bound(self) -> RawConstant:
        """Returns upper bound of the expression."""

    def __abs__(self) -> Expression:
        """Returns an absolute value of the expression."""
        return self if self.is_positive() else -self

    @abstractmethod
    def __add__(self, other: Union[RawConstant, Expression]) -> Expression:
        """Returns sum of the expression with the other."""

    def __ceil__(self) -> int:
        """Return the ceiling of the expression."""
        return math.ceil(self.upper_bound())

    def __floor__(self) -> int:
        """Return the floor of the expression."""
        return math.floor(self.lower_bound())

    def __floordiv__(self, other: Union[RawConstant, Expression]) -> int:
        """Returns quotient of the division of the expression by the other."""
        return (self / other).__floor__()

    @overload
    def __ge__(self, other: Union[RawConstant, Expression]) -> bool:
        ...

    @overload
    def __ge__(self, other: Any) -> Any:
        ...

    def __ge__(self, other: Any) -> Any:
        """Checks if the expression is greater than or equal to the other."""
        from .constant import (Infinite,
                               try_to_constant)
        other = try_to_constant(other)
        return ((other <= self
                 if isinstance(other, Infinite)
                 else not (other - self).is_positive())
                if isinstance(other, Expression)
                else NotImplemented)

    @overload
    def __gt__(self, other: Union[RawConstant, Expression]) -> bool:
        ...

    @overload
    def __gt__(self, other: Any) -> Any:
        ...

    def __gt__(self, other: Any) -> Any:
        """Checks if the expression is greater than the other."""
        from .constant import (Infinite,
                               try_to_constant)
        other = try_to_constant(other)
        return ((other < self
                 if isinstance(other, Infinite)
                 else (self - other).is_positive())
                if isinstance(other, Expression)
                else NotImplemented)

    @abstractmethod
    def __hash__(self) -> int:
        """Returns hash value of the expression."""

    @overload
    def __le__(self, other: Union[RawConstant, Expression]) -> bool:
        ...

    @overload
    def __le__(self, other: Any) -> Any:
        ...

    def __le__(self, other: Any) -> Any:
        """Checks if the expression is lower than or equal to the other."""
        from .constant import (Infinite,
                               try_to_constant)
        other = try_to_constant(other)
        return ((other >= self
                 if isinstance(other, Infinite)
                 else not (self - other).is_positive())
                if isinstance(other, Expression)
                else NotImplemented)

    @overload
    def __lt__(self, other: Union[RawConstant, Expression]) -> bool:
        ...

    @overload
    def __lt__(self, other: Any) -> Any:
        ...

    def __lt__(self, other: Any) -> Any:
        """Checks if the expression is lower than the other."""
        from .constant import (Infinite,
                               try_to_constant)
        other = try_to_constant(other)
        return ((other > self
                 if isinstance(other, Infinite)
                 else (other - self).is_positive())
                if isinstance(other, Expression)
                else NotImplemented)

    def __mod__(self, other: Union[RawConstant, Expression]) -> Expression:
        """Returns remainder of the division of the expression by the other."""
        return self - other * (self // other)

    @abstractmethod
    def __mul__(self, other: Union[RawConstant, Expression]) -> Expression:
        """Returns multiplication of the expression with the other."""

    @abstractmethod
    def __neg__(self) -> Expression:
        """Returns the expression negated."""

    def __pos__(self) -> Expression:
        """Returns the expression positive."""
        return self

    def __pow__(self, exponent: int) -> Expression:
        """Returns the expression raised to the given exponent."""
        if not isinstance(exponent, int):
            return NotImplemented
        from .constant import ONE
        if not exponent:
            return ONE
        result, step = ONE, self
        if exponent < 0:
            exponent, step = -exponent, step.inverse()
        while exponent > 1:
            if exponent & 1:
                result *= step
            step = step.square()
            exponent >>= 1
        result *= step
        return result

    @abstractmethod
    def __radd__(self, other: Union[RawConstant, Expression]) -> Expression:
        """Returns sum of the other with the expression."""

    def __rfloordiv__(self, other: Union[RawConstant, Expression]) -> int:
        """Returns quotient of the division of the other by the expression."""
        return (other / self).__floor__()

    def __rmod__(self, other: Union[RawConstant, Expression]) -> Expression:
        """Returns remainder of the division of the other by the expression."""
        return other - self * (other // self)

    @abstractmethod
    def __rmul__(self, other: Union[RawConstant, Expression]) -> Expression:
        """Returns multiplication of the other with the expression."""

    def __round__(self,
                  precision: Optional[int] = None) -> Union[int, Fraction]:
        """Returns the expression rounded to the given precision."""
        scale = BASE ** (1 if precision is None else precision + 1)
        return round(cast(Fraction, int(scale * self) / scale), precision)

    @overload
    def __rsub__(self, other: Union[RawConstant, Expression]) -> Expression:
        ...

    @overload
    def __rsub__(self, other: Any) -> Any:
        ...

    def __rsub__(self, other: Any) -> Any:
        """Returns difference of the other with the expression."""
        from .constant import try_to_constant
        other = try_to_constant(other)
        return (other + (-self)
                if isinstance(other, Expression)
                else NotImplemented)

    @overload
    def __rtruediv__(self,
                     other: Union[Expression, RawConstant]) -> Expression:
        ...

    @overload
    def __rtruediv__(self, other: Any) -> Any:
        ...

    def __rtruediv__(self, other: Any) -> Any:
        """Returns division of the other by the expression."""
        return (self.inverse() * other
                if isinstance(other, (Rational, float))
                else NotImplemented)

    @overload
    def __sub__(self, other: Union[RawConstant, Expression]) -> Expression:
        ...

    @overload
    def __sub__(self, other: Any) -> Any:
        ...

    def __sub__(self, other: Any) -> Any:
        """Returns difference of the expression with the other."""
        from .constant import try_to_constant
        other = try_to_constant(other)
        return (self + (-other)
                if isinstance(other, Expression)
                else NotImplemented)

    @overload
    def __truediv__(self: _Self, other: RawFinite) -> _Self:
        ...

    @overload
    def __truediv__(self, other: Union[Expression, RawUnbound]) -> Expression:
        ...

    def __truediv__(self, other: Any) -> Any:
        """Returns division of the expression by the other."""
        from .constant import try_to_constant
        other = try_to_constant(other)
        return (self * other.inverse()
                if isinstance(other, Expression)
                else NotImplemented)

    def __trunc__(self) -> int:
        """Returns the expression truncated to a nearest-to-zero integer."""
        return self.__floor__() if self.is_positive() else self.__ceil__()
