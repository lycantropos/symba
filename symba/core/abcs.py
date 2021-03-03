from abc import (ABC,
                 abstractmethod)
from numbers import Real
from typing import (Optional,
                    Union)

from .hints import SquareRooter


class Expression(ABC):
    @abstractmethod
    def __abs__(self) -> 'Expression':
        """Returns an absolute value of the expression."""

    @abstractmethod
    def __add__(self, other: Union[Real, 'Expression']) -> 'Expression':
        """Returns sum of the expression with the other."""

    @abstractmethod
    def __ge__(self, other: Union[Real, 'Expression']) -> bool:
        """Checks if the expression is greater than or equal to the other."""

    @abstractmethod
    def __gt__(self, other: Union[Real, 'Expression']) -> bool:
        """Checks if the expression is greater than the other."""

    @abstractmethod
    def __le__(self, other: Union[Real, 'Expression']) -> bool:
        """Checks if the expression is lower than or equal to the other."""

    @abstractmethod
    def __lt__(self, other: Union[Real, 'Expression']) -> bool:
        """Checks if the expression is lower than the other."""

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
    def __rmul__(self, other: Union[Real, 'Expression']) -> 'Expression':
        """Returns multiplication of the other with the expression."""

    def __rsub__(self, other: Union[Real, 'Expression']) -> 'Expression':
        """Returns difference of the other with the expression."""
        return other + (-self)

    def __sub__(self, other: Union[Real, 'Expression']) -> 'Expression':
        """Returns difference of the expression with the other."""
        return self + (-other)

    @abstractmethod
    def __truediv__(self, other: Union[Real, 'Expression']) -> 'Expression':
        """Returns division of the expression by the other."""

    @abstractmethod
    def __rtruediv__(self, other: Union[Real, 'Expression']) -> 'Expression':
        """Returns division of the expression by the other."""

    @abstractmethod
    def evaluate(self, square_rooter: Optional[SquareRooter] = None) -> Real:
        """Evaluates the expression."""
