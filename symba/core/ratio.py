from numbers import (Rational,
                     Real)
from typing import (Any,
                    Optional,
                    Union)

from reprit.base import generate_repr

from .abcs import Expression
from .constant import Zero
from .form import Form
from .hints import SquareRooter
from .utils import square


class Ratio(Expression):
    __slots__ = 'denominator', 'numerator'

    @classmethod
    def from_components(cls,
                        numerator: Expression,
                        denominator: Form) -> Expression:
        if not denominator.is_positive():
            numerator, denominator = -numerator, -denominator
        return (numerator.numerator / (denominator * numerator.denominator)
                if isinstance(numerator, Ratio)
                else cls(numerator, denominator)) if numerator else Zero

    def evaluate(self, square_rooter: Optional[SquareRooter] = None) -> Real:
        return (self.numerator.evaluate(square_rooter)
                / self.denominator.evaluate(square_rooter))

    def is_positive(self) -> bool:
        return self.numerator.is_positive()

    def lower_bound(self) -> Rational:
        return (self.numerator / self.denominator.upper_bound()).lower_bound()

    def perfect_scale_sqrt(self) -> Rational:
        return (self.numerator.perfect_scale_sqrt()
                / self.denominator.perfect_scale_sqrt())

    def upper_bound(self) -> Rational:
        return (self.numerator / self.denominator.lower_bound()).upper_bound()

    def __init__(self, numerator: Expression, denominator: Form) -> None:
        self.numerator, self.denominator = numerator, denominator

    def __add__(self, other: Union[Real, Expression]) -> Expression:
        return ((self.numerator * other.denominator
                 + other.numerator * self.denominator)
                / (self.denominator * other.denominator)
                if isinstance(other, Ratio)
                else Ratio.from_components(self.numerator
                                           + other * self.denominator,
                                           self.denominator))

    def __abs__(self) -> 'Ratio':
        return Ratio(abs(self.numerator), self.denominator)

    def __eq__(self, other: Any) -> Any:
        return (self.numerator == other.numerator
                if isinstance(other, Ratio)
                else (False
                      if isinstance(other, (Real, Expression))
                      else NotImplemented))

    def __hash__(self) -> int:
        return hash((self.numerator, self.denominator))

    def __mul__(self, other: Union[Real, Expression]) -> Expression:
        return ((self.numerator * other.numerator)
                / (self.denominator * other.denominator)
                if isinstance(other, Ratio)
                else (Ratio.from_components(self.numerator * other,
                                            self.denominator)
                      if isinstance(other, (Real, Expression))
                      else NotImplemented))

    def __neg__(self) -> Expression:
        return Ratio(-self.numerator, self.denominator)

    def __radd__(self, other: Union[Real, Expression]) -> Expression:
        return Ratio.from_components(self.numerator + other * self.denominator,
                                     self.denominator)

    __repr__ = generate_repr(__init__)

    def __rmul__(self, other: Union[Real, Expression]) -> Expression:
        return (Ratio.from_components(self.numerator * other, self.denominator)
                if isinstance(other, (Real, Expression))
                else NotImplemented)

    def __rtruediv__(self, other: Union[Real, Expression]) -> Expression:
        return ((self.denominator * other) / self.numerator
                if isinstance(other, (Real, Expression))
                else NotImplemented)

    def __str__(self) -> str:
        return '{} / ({})'.format('({})'.format(self.numerator)
                                  if isinstance(self.numerator, Form)
                                  else self.numerator,
                                  self.denominator)

    def __truediv__(self, other: Union[Real, Expression]) -> Expression:
        return ((self.numerator * other.denominator)
                / (self.denominator * other.numerator)
                if isinstance(other, Ratio)
                else (self.numerator / (self.denominator * other)
                      if isinstance(other, (Real, Expression))
                      else NotImplemented))
