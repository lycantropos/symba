from numbers import Real
from typing import (Optional,
                    Union)

from reprit.base import generate_repr

from .abcs import Expression
from .constant import (Constant,
                       Zero)
from .form import (Form,
                   is_form_positive)
from .hints import SquareRooter
from .term import Term


class Ratio(Expression):
    __slots__ = 'denominator', 'numerator'

    @classmethod
    def from_components(cls,
                        numerator: Union[Constant, Term, Form],
                        denominator: Form) -> Union[Constant, 'Ratio']:
        if not is_form_positive(denominator):
            numerator, denominator = -numerator, -denominator
        return cls(numerator, denominator) if numerator else Zero

    def __init__(self,
                 numerator: Union[Constant, Term, Form],
                 denominator: Form) -> None:
        self.numerator, self.denominator = numerator, denominator

    def __add__(self, other: Union[Constant, Term, Form, 'Ratio']
                ) -> Union[Constant, 'Ratio']:
        return (Ratio.from_components(self.numerator * other.denominator
                                      + other.numerator * self.denominator,
                                      self.denominator * other.denominator)
                if isinstance(other, Ratio)
                else Ratio.from_components(self.numerator
                                           + other * self.denominator,
                                           self.denominator))

    def __abs__(self) -> 'Ratio':
        return Ratio(abs(self.numerator), self.denominator)

    def __ge__(self, other: Union[Real, 'Expression']) -> bool:
        return (self.numerator * other.denominator
                >= self.denominator * other.numerator
                if isinstance(other, Ratio)
                else (self.numerator >= self.denominator * other
                      if isinstance(other, (Real, Expression))
                      else NotImplemented))

    def __gt__(self, other: Union[Real, Constant, Term, Form, 'Ratio']
               ) -> bool:
        return (self.numerator * other.denominator
                > self.denominator * other.numerator
                if isinstance(other, Ratio)
                else (self.numerator > self.denominator * other
                      if isinstance(other, (Real, Expression))
                      else NotImplemented))

    def __le__(self, other: Union[Real, 'Expression']) -> bool:
        return (self.numerator * other.denominator
                <= self.denominator * other.numerator
                if isinstance(other, Ratio)
                else (self.numerator <= self.denominator * other
                      if isinstance(other, (Real, Expression))
                      else NotImplemented))

    def __lt__(self, other: Union[Real, Constant, Term, Form, 'Ratio']
               ) -> bool:
        return (self.numerator * other.denominator
                < self.denominator * other.numerator
                if isinstance(other, Ratio)
                else (self.numerator < self.denominator * other
                      if isinstance(other, (Real, Expression))
                      else NotImplemented))

    def __neg__(self) -> 'Expression':
        return Ratio(-self.numerator, self.denominator)

    def __radd__(self, other: Union[Constant, Term, Form]
                 ) -> Union[Constant, 'Ratio']:
        return Ratio.from_components(self.numerator + other * self.denominator,
                                     self.denominator)

    __repr__ = generate_repr(__init__)

    def __str__(self) -> str:
        return '{} / ({})'.format('({})'.format(self.numerator)
                                  if isinstance(self.numerator, Form)
                                  else self.numerator,
                                  self.denominator)

    def evaluate(self, square_rooter: Optional[SquareRooter] = None) -> Real:
        return (self.numerator.evaluate(square_rooter)
                / self.denominator.evaluate(square_rooter))
