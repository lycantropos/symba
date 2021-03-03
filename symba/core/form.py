from collections import defaultdict
from numbers import Real
from typing import (TYPE_CHECKING,
                    Optional,
                    Union)

from reprit.base import generate_repr

from .abcs import Expression
from .constant import (Constant,
                       Zero)
from .hints import SquareRooter
from .term import (Term,
                   term_ceil,
                   term_floor)
from .utils import square

if TYPE_CHECKING:
    from .ratio import Ratio


class Form(Expression):
    __slots__ = 'tail', 'terms'

    @classmethod
    def from_components(cls,
                        *terms: Term,
                        tail: Constant = Zero
                        ) -> Union[Constant, Term, 'Form']:
        arguments_scales = defaultdict(Constant)
        for term in terms:
            arguments_scales[term.argument] += term.scale
        terms = list(filter(None,
                            [Term(scale, argument)
                             for argument, scale in arguments_scales.items()
                             if argument and scale]))
        return ((cls(*terms,
                     tail=tail)
                 if tail or len(terms) > 1
                 else terms[0])
                if terms
                else tail)

    def __init__(self, *terms: Term, tail: Constant = Zero) -> None:
        assert all(isinstance(term, Term) for term in terms)
        assert isinstance(tail, Constant)
        self.terms, self.tail = terms, tail

    def __abs__(self) -> 'Form':
        return self if is_form_positive(self) else -self

    def __add__(self, other: Union[Real, Constant, Term, 'Form']
                ) -> Union[Constant, 'Form']:
        return (Form.from_components(*self.terms,
                                     tail=self.tail + other)
                if isinstance(other, (Real, Constant))
                else (Form.from_components(*self.terms, other,
                                           tail=self.tail)
                      if isinstance(other, Term)
                      else (Form.from_components(*self.terms, *other.terms,
                                                 tail=self.tail + other.tail)
                            if isinstance(other, Form)
                            else NotImplemented)))

    def __eq__(self, other: 'Form') -> bool:
        return (self is other
                or (self.tail == other.tail
                    and len(self.terms) == len(other.terms)
                    and sorted(self.terms) == sorted(other.terms))
                if isinstance(other, Form)
                else (False
                      if isinstance(other, (Real, Constant, Term))
                      else NotImplemented))

    def __ge__(self, other: Union[Real, 'Expression']) -> bool:
        return (not _is_positive(other - self)
                if isinstance(other, (Real, Constant, Term, Form))
                else NotImplemented)

    def __gt__(self, other: Union[Real, Constant, Term, 'Form']) -> bool:
        return (_is_positive(self - other)
                if isinstance(other, (Real, Constant, Term, Form))
                else NotImplemented)

    def __hash__(self) -> int:
        return hash((self.terms, self.tail))

    def __le__(self, other: Union[Real, Constant, Term, 'Form']) -> bool:
        return (not _is_positive(self - other)
                if isinstance(other, (Real, Constant, Term, Form))
                else NotImplemented)

    def __lt__(self, other: Union[Real, Constant, Term, 'Form']) -> bool:
        return (_is_positive(other - self)
                if isinstance(other, (Real, Constant, Term, Form))
                else NotImplemented)

    def __mul__(self, other: Union[Real, Constant, Term, 'Form']
                ) -> Union[Constant, 'Form']:
        return (((self._square()
                  if self == other
                  else sum([term * other for term in self.terms],
                           self.tail * other))
                 if other
                 else Zero)
                if isinstance(other, (Real, Constant, Term, Form))
                else NotImplemented)

    def __neg__(self) -> 'Form':
        return Form(*[-term for term in self.terms],
                    tail=-self.tail)

    def __radd__(self, other: Union[Real, Constant, Term]
                 ) -> Union[Constant, 'Form']:
        return (Form.from_components(*self.terms,
                                     tail=other + self.tail)
                if isinstance(other, (Real, Constant))
                else (Form.from_components(other, *self.terms,
                                           tail=self.tail)
                      if isinstance(other, Term)
                      else NotImplemented))

    __repr__ = generate_repr(__init__)

    def __rmul__(self, other: Union[Real, Constant, Term]
                 ) -> Union[Constant, 'Form']:
        return ((sum([term * other for term in self.terms],
                     self.tail * other)
                 if other
                 else Zero)
                if isinstance(other, (Real, Constant, Term))
                else NotImplemented)

    def __rsub__(self, other: Union[Real, Constant, Term]
                 ) -> Union[Constant, 'Form']:
        return (other + (-self)
                if isinstance(other, (Real, Constant, Term))
                else NotImplemented)

    def __rtruediv__(self, other: Union[Real, Constant, Term]
                     ) -> Union[Constant, 'Form', 'Ratio']:
        components = (*self.terms, self.tail) if self.tail else self.terms
        components_count = len(components)
        if components_count > 2:
            from .ratio import Ratio
            return Ratio.from_components(Constant(other)
                                         if isinstance(other, Real)
                                         else other,
                                         self)
        subtrahend, minuend = components[0], components[1]
        return ((other * (subtrahend - minuend))
                / (square(subtrahend) - square(minuend)))

    def __str__(self) -> str:
        return (str(self.terms[0])
                + (' ' + ' '.join(map(_to_signed_value, self.terms[1:]))
                   if len(self.terms) > 1
                   else '')
                + (' ' + _to_signed_value(self.tail)
                   if self.tail
                   else ''))

    def __sub__(self, other: Union[Real, Constant, Term, 'Form']
                ) -> Union[Constant, Term, 'Form']:
        return (self + (-other)
                if isinstance(other, (Real, Constant, Term, Form))
                else NotImplemented)

    def __truediv__(self, other: Union[Real, Constant, Term, 'Form']
                    ) -> Union[Constant, 'Form']:
        from .ratio import Ratio
        return (Form(*[term / other for term in self.terms],
                     tail=self.tail / other)
                if isinstance(other, (Real, Constant))
                else (sum([term / other for term in self.terms],
                          self.tail / other)
                      if isinstance(other, Term)
                      else (Ratio.from_components(self, other)
                            if isinstance(other, Form)
                            else NotImplemented)))

    def evaluate(self, square_rooter: Optional[SquareRooter] = None) -> Real:
        return sum([term.evaluate(square_rooter) for term in self.terms],
                   self.tail.evaluate(square_rooter))

    def _square(self) -> 'Form':
        return sum([2 * (self.terms[step] * self.terms[index])
                    for step in range(1, len(self.terms))
                    for index in range(step)]
                   + ([(2 * self.tail) * term for term in self.terms]
                      if self.tail
                      else [])
                   + [square(term) for term in self.terms],
                   square(self.tail))


def form_ceil(value: Form) -> Constant:
    return sum([term_ceil(term) for term in value.terms], value.tail)


def form_floor(value: Form) -> Constant:
    return sum([term_floor(term) for term in value.terms], value.tail)


def is_form_positive(value: Form) -> bool:
    components = (*value.terms, value.tail) if value.tail else value.terms
    positive, negative = [], []
    for component in components:
        if component > Zero:
            positive.append(component)
        else:
            negative.append(component)
    if not (positive and negative):
        return not negative
    positive_count, negative_count = len(positive), len(negative)
    positive_squares_sum, negative_squares_sum = (
        sum(map(square, positive)), sum(map(square, negative)))
    if not _is_positive(positive_count * positive_squares_sum
                        - negative_squares_sum):
        return False
    elif _is_positive(positive_squares_sum
                      - negative_count * negative_squares_sum):
        return True
    if not form_ceil(value) > Zero:
        return False
    elif form_floor(value) >= Zero:
        return True
    return not is_form_positive(-value)


def _is_positive(value: Union[Constant, Term, Form]) -> bool:
    return (is_form_positive(value)
            if isinstance(value, Form)
            else value > Zero)


def _to_signed_value(value: Union[Constant, Term]) -> str:
    return ('+ ' + str(value)
            if value > 0
            else '- ' + str(-value))
