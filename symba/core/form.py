from collections import defaultdict
from functools import reduce
from numbers import (Rational,
                     Real)
from typing import (TYPE_CHECKING,
                    Any,
                    Dict,
                    Optional,
                    Union)

from reprit.base import generate_repr

from .abcs import Expression
from .constant import (Constant,
                       Zero)
from .hints import SquareRooter
from .term import Term
from .utils import (lcm,
                    square)

if TYPE_CHECKING:
    from .ratio import Ratio


class Form(Expression):
    __slots__ = 'tail', 'terms'

    @classmethod
    def from_components(cls,
                        *terms: Term,
                        tail: Constant = Zero
                        ) -> Union[Constant, Term, 'Form']:
        arguments_scales = (defaultdict
                            (Constant))  # type: Dict[Expression, Constant]
        for term in terms:
            arguments_scales[term.argument] += term.scale
        terms = tuple(filter(None,
                             [Term(scale, argument)
                              for argument, scale in arguments_scales.items()
                              if argument and scale]))
        return ((cls(*terms,
                     tail=tail)
                 if tail or len(terms) > 1
                 else terms[0])
                if terms
                else tail)

    def evaluate(self, square_rooter: Optional[SquareRooter] = None) -> Real:
        return sum([term.evaluate(square_rooter) for term in self.terms],
                   self.tail.evaluate(square_rooter))

    def is_positive(self) -> bool:
        components = (*self.terms, self.tail) if self.tail else self.terms
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
        if not (positive_count * positive_squares_sum
                - negative_squares_sum).is_positive():
            return False
        elif (positive_squares_sum
              - negative_count * negative_squares_sum).is_positive():
            return True
        elif not (negative_count * negative_squares_sum
                  - positive_squares_sum).is_positive():
            return True
        elif (negative_squares_sum
              - positive_count * positive_squares_sum).is_positive():
            return False
        return self.upper_bound() > 0 and self.lower_bound() >= 0

    def lower_bound(self) -> Rational:
        common_denominator = (self._common_denominator()
                              * 10 ** (len(self.terms) + bool(self.tail)))
        return (sum([(common_denominator * term).lower_bound()
                     for term in self.terms],
                    (common_denominator * self.tail).lower_bound())
                / common_denominator)

    def upper_bound(self) -> Rational:
        common_denominator = (self._common_denominator()
                              * 10 ** (len(self.terms) + bool(self.tail)))
        return (sum([(common_denominator * term).upper_bound()
                     for term in self.terms],
                    (common_denominator * self.tail).upper_bound())
                / common_denominator)

    def _common_denominator(self) -> int:
        terms_scales_denominators = [term.scale.value.denominator
                                     for term in self.terms]
        return (reduce(lcm, terms_scales_denominators,
                       self.tail.value.denominator)
                if self.tail
                else reduce(lcm, terms_scales_denominators))

    def __init__(self, *terms: Term, tail: Constant = Zero) -> None:
        assert all(isinstance(term, Term) for term in terms)
        assert isinstance(tail, Constant)
        self.terms, self.tail = terms, tail

    def __abs__(self) -> 'Form':
        return self if self.is_positive() else -self

    def __add__(self, other: Union[Real, Expression]) -> Expression:
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

    def __eq__(self, other: Any) -> Any:
        return (self is other
                or (self.tail == other.tail
                    and len(self.terms) == len(other.terms)
                    and set(self.terms) == set(other.terms))
                if isinstance(other, Form)
                else (False
                      if isinstance(other, (Real, Expression))
                      else NotImplemented))

    def __hash__(self) -> int:
        return hash((self.terms, self.tail))

    def __mul__(self, other: Union[Real, Expression]) -> Expression:
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

    def __radd__(self, other: Union[Real, Expression]) -> Expression:
        return (Form.from_components(*self.terms,
                                     tail=other + self.tail)
                if isinstance(other, (Real, Constant))
                else (Form.from_components(other, *self.terms,
                                           tail=self.tail)
                      if isinstance(other, Term)
                      else NotImplemented))

    __repr__ = generate_repr(__init__)

    def __rmul__(self, other: Union[Real, Expression]) -> Expression:
        return ((sum([term * other for term in self.terms],
                     self.tail * other)
                 if other
                 else Zero)
                if isinstance(other, (Real, Constant, Term))
                else NotImplemented)

    def __rtruediv__(self, other: Union[Real, Expression]) -> Expression:
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

    def __truediv__(self, other: Union[Real, Expression]) -> Expression:
        return (Form(*[term / other for term in self.terms],
                     tail=self.tail / other)
                if isinstance(other, (Real, Constant))
                else (sum([term / other for term in self.terms],
                          self.tail / other)
                      if isinstance(other, Term)
                      else (self._divide_by_form(other)
                            if isinstance(other, Form)
                            else NotImplemented)))

    def _divide_by_form(self, other: 'Form') -> Expression:
        has_tail = bool(self.tail)
        if (has_tail is bool(other.tail)
                and len(self.terms) == len(other.terms)):
            terms_scales = {term.argument: term.scale for term in self.terms}
            other_terms_scales = {term.argument: term.scale
                                  for term in other.terms}
            if terms_scales.keys() == other_terms_scales.keys():
                scales_ratios = (scale / other_terms_scales[term]
                                 for term, scale in terms_scales.items())
                first_scales_ratio = (self.tail / other.tail
                                      if has_tail
                                      else next(scales_ratios))
                if all(scales_ratio == first_scales_ratio
                       for scales_ratio in scales_ratios):
                    return first_scales_ratio
        from .ratio import Ratio
        return Ratio.from_components(self, other)

    def _square(self) -> Expression:
        return sum([2 * (self.terms[step] * self.terms[index])
                    for step in range(1, len(self.terms))
                    for index in range(step)]
                   + ([(2 * self.tail) * term for term in self.terms]
                      if self.tail
                      else [])
                   + [square(term) for term in self.terms],
                   square(self.tail))


def _to_signed_value(value: Union[Constant, Term]) -> str:
    return '+ ' + str(value) if value.is_positive() else '- ' + str(-value)
