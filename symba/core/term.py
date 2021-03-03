import math
from numbers import Real
from typing import (TYPE_CHECKING,
                    Optional,
                    Union)

from reprit.base import generate_repr

from symba.core.utils import (sqrt_floor,
                              square)
from .abcs import Expression
from .constant import (Constant,
                       One,
                       Zero,
                       constant_sqrt_ceil,
                       constant_sqrt_floor)
from .hints import SquareRooter

if TYPE_CHECKING:
    from .form import Form


class Term(Expression):
    __slots__ = 'argument', 'scale'

    @classmethod
    def from_components(cls,
                        scale: Constant,
                        argument: Expression) -> Union[Constant, 'Term']:
        if not (scale and argument):
            return Zero
        if isinstance(argument, Constant):
            argument_value = argument.value
            argument_numerator = argument_value.numerator
            argument_numerator_sqrt_floor = sqrt_floor(argument_numerator)
            if square(argument_numerator_sqrt_floor) == argument_numerator:
                scale *= argument_numerator_sqrt_floor
                argument /= argument_numerator
            argument_denominator = argument_value.denominator
            argument_denominator_sqrt_floor = sqrt_floor(argument_denominator)
            if square(argument_denominator_sqrt_floor) == argument_denominator:
                scale /= argument_denominator_sqrt_floor
                argument *= argument_denominator
                if argument == One:
                    return scale
            elif argument_denominator != 1:
                scale /= argument_denominator
                argument = Constant(argument_numerator * argument_denominator)
        return cls(scale, argument)

    def __init__(self,
                 scale: Constant,
                 argument: Union[Constant, 'Term', 'Form']) -> None:
        self.scale, self.argument = scale, argument

    def __abs__(self) -> 'Expression':
        return Term(abs(self.scale), self.argument)

    def __add__(self, other: Union[Real, Constant, 'Term']) -> 'Form':
        from .form import Form
        return (Form.from_components(self,
                                     tail=Constant(other))
                if isinstance(other, Real)
                else (Form.from_components(self,
                                           tail=other)
                      if isinstance(other, Constant)
                      else (Form.from_components(self, other)
                            if isinstance(other, Term)
                            else NotImplemented)))

    def __eq__(self, other: 'Term') -> bool:
        return (self.scale == other.scale and self.argument == other.argument
                if isinstance(other, Term)
                else NotImplemented)

    def __ge__(self, other: Union[Real, Constant, 'Term']) -> bool:
        return (((other <= 0
                  or square(other) <= square(self.scale) * self.argument)
                 if self.scale > 0
                 else
                 (other <= 0
                  and square(other) >= square(self.scale) * self.argument))
                if isinstance(other, (Real, Constant, Term))
                else NotImplemented)

    def __gt__(self, other: Union[Real, Constant, 'Term']) -> bool:
        return (((other <= 0
                  or square(other) < square(self.scale) * self.argument)
                 if self.scale > 0
                 else (other <= 0
                       and square(other) > square(
                        self.scale) * self.argument))
                if isinstance(other, (Real, Constant, Term))
                else NotImplemented)

    def __hash__(self) -> int:
        return hash((self.scale, self.argument))

    def __le__(self, other: Union[Real, Constant, 'Term']) -> bool:
        return (((other > 0
                  and square(other) >= square(self.scale) * self.argument)
                 if self.scale > 0
                 else other > 0 or (square(other)
                                    <= square(self.scale) * self.argument))
                if isinstance(other, (Real, Constant, Term))
                else NotImplemented)

    def __lt__(self, other: Union[Real, Constant, 'Term']) -> bool:
        return (((other > 0
                  and square(other) > square(self.scale) * self.argument)
                 if self.scale > 0
                 else (other > 0
                       or square(other) < square(self.scale) * self.argument))
                if isinstance(other, (Real, Constant, Term))
                else NotImplemented)

    def __mul__(self, other: Union[Real, Constant, 'Term']
                ) -> Union[Constant, 'Term']:
        return ((Term(self.scale * other, self.argument)
                 if other
                 else Zero)
                if isinstance(other, (Real, Constant))
                else (self._multiply_with_term(other)
                      if isinstance(other, Term)
                      else NotImplemented))

    def __neg__(self) -> 'Term':
        return Term(-self.scale, self.argument)

    def __radd__(self, other: Union[Real, Constant, 'Term']) -> 'Form':
        from .form import Form
        return (Form.from_components(self,
                                     tail=Constant(other))
                if isinstance(other, Real)
                else (Form.from_components(self,
                                           tail=other)
                      if isinstance(other, Constant)
                      else NotImplemented))

    __repr__ = generate_repr(__init__)

    def __rmul__(self, other: Union[Real, Constant]
                 ) -> Union[Constant, 'Term']:
        return ((Term(self.scale * other, self.argument)
                 if other
                 else Zero)
                if isinstance(other, (Real, Constant))
                else NotImplemented)

    def __rsub__(self, other: Union[Real, Constant]) -> 'Form':
        return (other + (-self)
                if isinstance(other, (Real, Constant))
                else NotImplemented)

    def __rtruediv__(self, other: Union[Real, Constant]) -> 'Term':
        return (Term.from_components(other / self.scale, One / self.argument)
                if isinstance(other, (Real, Constant))
                else NotImplemented)

    def __str__(self) -> str:
        return ((''
                 if self.scale == One
                 else ('-'
                       if self.scale == -One
                       else '{} * '.format(self.scale)))
                + 'sqrt({})'.format(self.argument))

    def __sub__(self, other: Union[Real, Constant, 'Term']) -> 'Form':
        return (self + (-other)
                if isinstance(other, (Real, Constant, Term))
                else NotImplemented)

    def __truediv__(self, other: Union[Real, Constant, 'Term']) -> 'Term':
        return (Term(self.scale / other, self.argument)
                if isinstance(other, (Real, Constant))
                else (self._multiply_with_term(One / other)
                      if isinstance(other, Term)
                      else NotImplemented))

    def evaluate(self, square_rooter: Optional[SquareRooter] = None) -> Real:
        return (self.scale.evaluate(square_rooter)
                * (math.sqrt
                   if square_rooter is None
                   else square_rooter)(self.argument.evaluate(square_rooter)))

    def _multiply_with_term(self, other: 'Term') -> Union[Constant, 'Term']:
        scale = self.scale * other.scale
        argument, other_argument = self.argument, other.argument
        if argument == other_argument:
            return scale * argument
        elif (isinstance(argument, Constant)
              and isinstance(other_argument, Constant)):
            arguments_gcd = math.gcd(argument.value.numerator,
                                     other_argument.value.numerator)
            argument /= arguments_gcd
            other_argument /= arguments_gcd
            scale *= arguments_gcd
        return Term.from_components(scale, argument * other_argument)


def term_floor(term: Term) -> Constant:
    if term < Zero:
        return -term_ceil(-term)
    argument = term.argument
    argument_floor = (constant_sqrt_floor
                      (argument
                       if isinstance(argument, Constant)
                       else (term_floor(argument)
                             if isinstance(argument, Term)
                             else (sum(map(term_floor, argument.terms),
                                       argument.tail)
                                   if isinstance(argument, Form)
                                   else NotImplemented))))
    assert not square(argument_floor) > argument
    return term.scale * argument_floor


def term_ceil(term: Term) -> Constant:
    if term < Zero:
        return -term_floor(-term)
    argument = term.argument
    argument_ceil = constant_sqrt_ceil(argument
                                       if isinstance(argument, Constant)
                                       else
                                       (term_ceil(argument)
                                        if isinstance(argument, Term)
                                        else
                                        (sum(map(term_ceil, argument.terms),
                                             argument.tail)
                                         if isinstance(argument, Form)
                                         else NotImplemented)))
    assert not square(argument_ceil) < argument
    return term.scale * argument_ceil
