import math
from abc import (ABC,
                 abstractmethod)
from numbers import (Rational,
                     Real)
from typing import (Optional,
                    Union)

from .hints import SquareRooter


class Expression(ABC):
    @abstractmethod
    def is_positive(self) -> bool:
        """Checks if the expression is positive."""

    @abstractmethod
    def evaluate(self, square_rooter: Optional[SquareRooter] = None) -> Real:
        """Evaluates the expression."""

    @abstractmethod
    def perfect_scale_sqrt(self) -> Rational:
        """Returns rational square root of scale of the expression."""

    @abstractmethod
    def lower_bound(self) -> Rational:
        """Returns lower bound of the expression."""

    @abstractmethod
    def significant_digits_count(self) -> int:
        """Returns significant digits count of the expression."""

    @abstractmethod
    def upper_bound(self) -> Rational:
        """Returns upper bound of the expression."""

    @abstractmethod
    def __abs__(self) -> 'Expression':
        """Returns an absolute value of the expression."""

    @abstractmethod
    def __add__(self, other: Union[Real, 'Expression']) -> 'Expression':
        """Returns sum of the expression with the other."""

    def __ceil__(self) -> int:
        """Return the ceiling of the expression."""
        return math.ceil(self.upper_bound())

    def __floor__(self) -> int:
        """Return the floor of the expression."""
        return math.floor(self.lower_bound())

    def __ge__(self, other: Union[Real, 'Expression']) -> bool:
        """Checks if the expression is greater than or equal to the other."""
        return (not (other - self).is_positive()
                if isinstance(other, (Real, Expression))
                else NotImplemented)

    def __gt__(self, other: Union[Real, 'Expression']) -> bool:
        """Checks if the expression is greater than the other."""
        return ((self - other).is_positive()
                if isinstance(other, (Real, Expression))
                else NotImplemented)

    @abstractmethod
    def __hash__(self) -> int:
        """Returns hash value of the expression."""

    def __le__(self, other: Union[Real, 'Expression']) -> bool:
        """Checks if the expression is lower than or equal to the other."""
        return (not (self - other).is_positive()
                if isinstance(other, (Real, Expression))
                else NotImplemented)

    def __lt__(self, other: Union[Real, 'Expression']) -> bool:
        """Checks if the expression is lower than the other."""
        return ((other - self).is_positive()
                if isinstance(other, (Real, Expression))
                else NotImplemented)

    @abstractmethod
    def __mul__(self, other: Union[Real, 'Expression']) -> 'Expression':
        """Returns multiplication of the expression with the other."""

    @abstractmethod
    def __neg__(self) -> 'Expression':
        """Returns the expression negated."""

    def __pos__(self) -> 'Expression':
        """Returns the expression positive."""
        return self

    @abstractmethod
    def __radd__(self, other: Union[Real, 'Expression']) -> 'Expression':
        """Returns sum of the other with the expression."""

    @abstractmethod
    def __rmul__(self, other: Union[Real, 'Expression']) -> 'Expression':
        """Returns multiplication of the other with the expression."""

    def __rsub__(self, other: Union[Real, 'Expression']) -> 'Expression':
        """Returns difference of the other with the expression."""
        return (other + (-self)
                if isinstance(other, (Real, Expression))
                else NotImplemented)

    def __sub__(self, other: Union[Real, 'Expression']) -> 'Expression':
        """Returns difference of the expression with the other."""
        return (self + (-other)
                if isinstance(other, (Real, Expression))
                else NotImplemented)

    @abstractmethod
    def __truediv__(self, other: Union[Real, 'Expression']) -> 'Expression':
        """Returns division of the expression by the other."""

    def __trunc__(self) -> int:
        return self.__floor__() if self.is_positive() else self.__ceil__()

    @abstractmethod
    def __rtruediv__(self, other: Union[Real, 'Expression']) -> 'Expression':
        """Returns division of the expression by the other."""
