import math
from collections import defaultdict
from functools import reduce
from numbers import (Rational,
                     Real)
from typing import (TYPE_CHECKING,
                    Any,
                    Dict,
                    Optional,
                    Sequence,
                    Union)

from reprit.base import generate_repr

from .abcs import Expression
from .constant import (Constant,
                       One,
                       Zero)
from .hints import SqrtEvaluator
from .term import Term
from .utils import (BASE,
                    lcm,
                    sqrt_floor,
                    square)

if TYPE_CHECKING:
    from .ratio import Ratio


class Form(Expression):
    @classmethod
    def from_components(cls,
                        *terms: Term,
                        tail: Constant = Zero
                        ) -> Union[Constant, Term, 'Form']:
        arguments_scales = (defaultdict
                            (Constant))  # type: Dict[Expression, Constant]
        queue = sorted(terms,
                       reverse=True)
        while queue:
            term = queue.pop()
            arguments_scales[term.argument] += term.scale
            next_queue = []
            for other in queue:
                ratio = other.argument / term.argument
                if isinstance(ratio, Constant):
                    ratio_sqrt = ratio.perfect_sqrt()
                    if ratio_sqrt.square() == ratio:
                        arguments_scales[term.argument] += (other.scale
                                                            * ratio_sqrt)
                        continue
                next_queue.append(other)
            queue = next_queue
        terms = tuple(Term(scale, argument)
                      for argument, scale in arguments_scales.items()
                      if scale)
        return ((cls(*terms,
                     tail=tail)
                 if tail or len(terms) > 1
                 else terms[0])
                if terms
                else tail)

    def __init__(self, *terms: Term, tail: Constant = Zero) -> None:
        self._terms, self._tail = terms, tail

    @property
    def tail(self) -> Constant:
        return self._tail

    @property
    def terms(self) -> Sequence[Term]:
        return self._terms

    def common_denominator(self) -> int:
        terms_scales_denominators = [term.scale.value.denominator
                                     for term in self.terms]
        return (reduce(lcm, terms_scales_denominators,
                       self.tail.value.denominator)
                if self.tail
                else reduce(lcm, terms_scales_denominators))

    def evaluate(self, sqrt_evaluator: Optional[SqrtEvaluator] = None) -> Real:
        return sum([term.evaluate(sqrt_evaluator) for term in self.terms],
                   self.tail.evaluate(sqrt_evaluator))

    def is_positive(self) -> bool:
        components = (*self.terms, self.tail) if self.tail else self.terms
        positive, negative = [], []
        for component in components:
            if component.is_positive():
                positive.append(component)
            else:
                negative.append(component)
        if not (positive and negative):
            return not negative
        positive_count, negative_count = len(positive), len(negative)
        positive_squares_sum, negative_squares_sum = (
            sum(component.square() for component in positive),
            sum(component.square() for component in negative))
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
        common_scale = self._common_scale()
        return sum([(common_scale * term).lower_bound()
                    for term in self.terms],
                   (common_scale * self.tail).lower_bound()) / common_scale

    def perfect_sqrt(self) -> Expression:
        terms_count = len(self.terms)
        components_discriminant = 1 + 8 * terms_count
        has_perfect_square_structure = (
                self.tail
                and (square(sqrt_floor(components_discriminant))
                     == components_discriminant))
        if not (all(isinstance(term.argument, Constant)
                    for term in self.terms)
                and (not has_perfect_square_structure or terms_count < 4)):
            raise ValueError('Unsupported value: {!r}.'.format(self))
        elif not has_perfect_square_structure:
            pass
        elif terms_count == 1:
            term = self.terms[0]
            discriminant = self.tail.square() - term.square()
            if discriminant > 0:
                # checking if the form can be represented as
                # ``(a * sqrt(x) + b * sqrt(y)) ** 2``,
                # where ``a, b, x, y`` are rational
                discriminant_sqrt = discriminant.perfect_sqrt()
                if discriminant_sqrt.square() == discriminant:
                    return (_positiveness_to_sign(term.is_positive())
                            * Term.from_components(
                                    One, (self.tail - discriminant_sqrt) / 2)
                            + Term.from_components(
                                    One, (self.tail + discriminant_sqrt) / 2))
            else:
                # checking if the form can be represented as
                # ``(a * sqrt(x * sqrt(x)) + b * sqrt(sqrt(x))) ** 2``,
                # where ``a, b, x`` are rational
                discriminant = (term.argument
                                * (term.scale.square() * term.argument
                                   - self.tail.square()))
                if discriminant > 0:
                    discriminant_sqrt = discriminant.perfect_sqrt()
                    if discriminant_sqrt.square() == discriminant:
                        for candidate_squared in ((term.scale * term.argument
                                                   + discriminant_sqrt) / 2,
                                                  (term.scale * term.argument
                                                   - discriminant_sqrt) / 2):
                            candidate = candidate_squared.perfect_sqrt()
                            if candidate.square() == candidate_squared:
                                three_fourth_scale = candidate / term.argument
                                one_fourth_scale = (self.tail
                                                    / (2 * three_fourth_scale
                                                       * term.argument))
                                one_fourth = Term(One, term.argument)
                                return Form(Term(three_fourth_scale,
                                                 term.argument * one_fourth),
                                            Term(one_fourth_scale, one_fourth))
        elif terms_count == 3:
            squared_candidates = sorted([
                self.terms[0] * self.terms[1] / (2 * self.terms[2]),
                self.terms[0] * self.terms[2] / (2 * self.terms[1]),
                self.terms[1] * self.terms[2] / (2 * self.terms[0])])
            if sum(squared_candidates) == self.tail:
                max_modulus_term = max(self.terms,
                                       key=abs)
                mid_max_components_same_sign = max_modulus_term.is_positive()
                min_modulus_term = min(self.terms,
                                       key=abs)
                min_mid_components_same_sign = min_modulus_term.is_positive()
                max_component_is_positive = (
                        mid_max_components_same_sign
                        or not min_mid_components_same_sign
                        or (squared_candidates[2]
                            > squared_candidates[0] + squared_candidates[1]))
                mid_component_is_positive = (max_component_is_positive
                                             is mid_max_components_same_sign)
                min_component_is_positive = (mid_component_is_positive
                                             is min_mid_components_same_sign)
                signs = [_positiveness_to_sign(min_component_is_positive),
                         _positiveness_to_sign(mid_component_is_positive),
                         _positiveness_to_sign(max_component_is_positive)]
                return sum(Term.from_components(sign * One, squared)
                           for sign, squared in zip(signs, squared_candidates))
        return (Constant(self._common_numerator())
                / self.common_denominator()).perfect_sqrt()

    def significant_digits_count(self) -> int:
        return max(max(term.significant_digits_count() for term in self.terms),
                   self.tail.significant_digits_count())

    def square(self) -> Expression:
        return sum([2 * (self.terms[step] * self.terms[index])
                    for step in range(1, len(self.terms))
                    for index in range(step)]
                   + ([(2 * self.tail) * term for term in self.terms]
                      if self.tail
                      else [])
                   + [term.square() for term in self.terms],
                   self.tail.square())

    def upper_bound(self) -> Rational:
        common_scale = self._common_scale()
        return sum([(common_scale * term).upper_bound()
                    for term in self.terms],
                   (common_scale * self.tail).upper_bound()) / common_scale

    __slots__ = '_tail', '_terms'

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
        return hash((frozenset(self.terms), self.tail))

    def __mul__(self, other: Union[Real, Expression]) -> Expression:
        return (((self.square()
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
                / (subtrahend.square() - minuend.square()))

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

    def _common_numerator(self) -> int:
        terms_scales_denominators = [term.scale.value.numerator
                                     for term in self.terms]
        return (reduce(math.gcd, terms_scales_denominators,
                       self.tail.value.numerator)
                if self.tail
                else reduce(math.gcd, terms_scales_denominators))

    def _common_scale(self) -> int:
        return (self.common_denominator()
                * BASE ** self.significant_digits_count())

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
        return self * (One / other)


def _positiveness_to_sign(flag: bool) -> int:
    return 2 * flag - 1


def _to_signed_value(value: Union[Constant, Term]) -> str:
    return '+ ' + str(value) if value.is_positive() else '- ' + str(-value)
