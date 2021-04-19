import math
from abc import (ABC,
                 abstractmethod)
from numbers import Real
from typing import (Optional,
                    Tuple,
                    Union)

from .hints import SqrtEvaluator
from .utils import (BASE,
                    to_binary_digits)


class Expression(ABC):
    __slots__ = ()

    @property
    @abstractmethod
    def degree(self) -> int:
        """Returns degree of the expression."""

    @property
    @abstractmethod
    def is_finite(self) -> bool:
        """Checks if the expression is finite."""

    @abstractmethod
    def evaluate(self, sqrt_evaluator: Optional[SqrtEvaluator] = None) -> Real:
        """Evaluates the expression."""

    @abstractmethod
    def extract_common_denominator(self) -> Tuple[int, 'Expression']:
        """
        Returns a pair of the common denominator of the expression
        and the rest of the expression.
        """

    @abstractmethod
    def extract_common_numerator(self) -> Tuple[int, 'Expression']:
        """
        Returns a pair of the common numerator of the expression
        and the rest of the expression.
        """

    @abstractmethod
    def inverse(self) -> 'Expression':
        """Returns the expression inverted."""

    @abstractmethod
    def is_positive(self) -> bool:
        """Checks if the expression is positive."""

    @abstractmethod
    def lower_bound(self) -> Real:
        """Returns lower bound of the expression."""

    @abstractmethod
    def perfect_sqrt(self) -> 'Expression':
        """Returns perfect square root part of the expression."""

    @abstractmethod
    def significant_digits_count(self) -> int:
        """Returns significant digits count of the expression."""

    @abstractmethod
    def square(self) -> 'Expression':
        """Returns the expression squared."""

    @abstractmethod
    def upper_bound(self) -> Real:
        """Returns upper bound of the expression."""

    def __abs__(self) -> 'Expression':
        """Returns an absolute value of the expression."""
        return self if self.is_positive() else -self

    @abstractmethod
    def __add__(self, other: Union[Real, 'Expression']) -> 'Expression':
        """Returns sum of the expression with the other."""

    def __ceil__(self) -> int:
        """Return the ceiling of the expression."""
        return math.ceil(self.upper_bound())

    def __floor__(self) -> int:
        """Return the floor of the expression."""
        return math.floor(self.lower_bound())

    def __floordiv__(self, other: Union[Real, 'Expression']) -> int:
        """Returns quotient of the division of the expression by the other."""
        return math.floor(self / other)

    def __ge__(self, other: Union[Real, 'Expression']) -> bool:
        """Checks if the expression is greater than or equal to the other."""
        from .constant import to_expression
        other = to_expression(other)
        return ((not (other - self).is_positive()
                 if other.is_finite
                 else other <= self)
                if isinstance(other, Expression)
                else NotImplemented)

    def __gt__(self, other: Union[Real, 'Expression']) -> bool:
        """Checks if the expression is greater than the other."""
        from .constant import to_expression
        other = to_expression(other)
        return (((self - other).is_positive()
                 if other.is_finite
                 else other < self)
                if isinstance(other, Expression)
                else NotImplemented)

    @abstractmethod
    def __hash__(self) -> int:
        """Returns hash value of the expression."""

    def __le__(self, other: Union[Real, 'Expression']) -> bool:
        """Checks if the expression is lower than or equal to the other."""
        from .constant import to_expression
        other = to_expression(other)
        return ((not (self - other).is_positive()
                 if other.is_finite
                 else other >= self)
                if isinstance(other, Expression)
                else NotImplemented)

    def __lt__(self, other: Union[Real, 'Expression']) -> bool:
        """Checks if the expression is lower than the other."""
        from .constant import to_expression
        other = to_expression(other)
        return (((other - self).is_positive()
                 if other.is_finite
                 else other > self)
                if isinstance(other, Expression)
                else NotImplemented)

    def __mod__(self, other: Union[Real, 'Expression']) -> 'Expression':
        """Returns remainder of the division of the expression by the other."""
        return self - other * (self // other)

    @abstractmethod
    def __mul__(self, other: Union[Real, 'Expression']) -> 'Expression':
        """Returns multiplication of the expression with the other."""

    @abstractmethod
    def __neg__(self) -> 'Expression':
        """Returns the expression negated."""

    def __pos__(self) -> 'Expression':
        """Returns the expression positive."""
        return self

    def __pow__(self, exponent: int) -> 'Expression':
        """Returns the expression raised to the given exponent."""
        if not isinstance(exponent, int):
            return NotImplemented
        from .constant import One
        result, step = One, self
        if exponent < 0:
            exponent, step = -exponent, step.inverse()
        for digit in to_binary_digits(exponent):
            if digit:
                result *= step
            step = step.square()
        return result

    @abstractmethod
    def __radd__(self, other: Union[Real, 'Expression']) -> 'Expression':
        """Returns sum of the other with the expression."""

    def __rfloordiv__(self, other: Union[Real, 'Expression']) -> int:
        """Returns quotient of the division of the other by the expression."""
        return math.floor(other / self)

    def __rmod__(self, other: Union[Real, 'Expression']) -> 'Expression':
        """Returns remainder of the division of the other by the expression."""
        return other - self * (other // self)

    @abstractmethod
    def __rmul__(self, other: Union[Real, 'Expression']) -> 'Expression':
        """Returns multiplication of the other with the expression."""

    def __round__(self, precision: Optional[int] = None) -> 'Expression':
        """Returns the expression rounded to the given precision."""
        scale = BASE ** (1 if precision is None else precision + 1)
        return round(int(scale * self) / scale, precision)

    def __rsub__(self, other: Union[Real, 'Expression']) -> 'Expression':
        """Returns difference of the other with the expression."""
        return (other + (-self)
                if isinstance(other, (Real, Expression))
                else NotImplemented)

    def __rtruediv__(self, other: Real) -> 'Expression':
        """Returns division of the other by the expression."""
        return (self.inverse() * other
                if isinstance(other, Real)
                else NotImplemented)

    def __sub__(self, other: Union[Real, 'Expression']) -> 'Expression':
        """Returns difference of the expression with the other."""
        return (self + (-other)
                if isinstance(other, (Real, Expression))
                else NotImplemented)

    def __truediv__(self, other: Union[Real, 'Expression']) -> 'Expression':
        """Returns division of the expression by the other."""
        from .constant import to_expression
        other = to_expression(other)
        return (self * other.inverse()
                if isinstance(other, Expression)
                else NotImplemented)

    def __trunc__(self) -> int:
        """Returns the expression truncated to a nearest-to-zero integer."""
        return self.__floor__() if self.is_positive() else self.__ceil__()
