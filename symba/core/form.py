import math
from collections import defaultdict
from functools import reduce
from numbers import (Rational,
                     Real)
from typing import (Any,
                    Dict,
                    Optional,
                    Sequence,
                    Tuple,
                    TypeVar,
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

    __slots__ = '_tail', '_terms'

    def __init__(self, *terms: Term, tail: Constant = Zero) -> None:
        self._tail, self._terms = tail, terms

    @property
    def tail(self) -> Constant:
        return self._tail

    @property
    def terms(self) -> Sequence[Term]:
        return self._terms

    def evaluate(self, sqrt_evaluator: Optional[SqrtEvaluator] = None) -> Real:
        return sum([term.evaluate(sqrt_evaluator) for term in self.terms],
                   self.tail.evaluate(sqrt_evaluator))

    def extract_common_denominator(self) -> Tuple[int, 'Form']:
        terms_common_denominators, _ = _transpose(
                [term.extract_common_denominator() for term in self.terms])
        tail_denominator, _ = self.tail.extract_common_denominator()
        common_denominator = reduce(lcm, terms_common_denominators,
                                    tail_denominator)
        return common_denominator, Form(*[term * common_denominator
                                          for term in self.terms],
                                        tail=self.tail * common_denominator)

    def extract_common_numerator(self) -> Tuple[int, 'Form']:
        terms_common_numerators, _ = _transpose(
                [term.extract_common_numerator() for term in self.terms])
        tail_numerator, _ = self.tail.extract_common_numerator()
        common_numerator = reduce(math.gcd, terms_common_numerators,
                                  tail_numerator)
        return common_numerator, Form(*[term / common_numerator
                                        for term in self.terms],
                                      tail=self.tail / common_numerator)

    def inverse(self) -> Expression:
        denominator, numerator = self, One
        for base_term in denominator.terms:
            non_divisible, divisible = [], []
            for term in denominator.terms:
                (non_divisible
                 if term.argument % base_term.argument
                 else divisible).append(term)
            if not divisible:
                continue
            numerator *= Form(*non_divisible, *[-term for term in divisible],
                              tail=denominator.tail)
            denominator = (
                    Form(*non_divisible,
                         tail=denominator.tail).square()
                    - base_term.argument
                    * Form(*[Term.from_components(term.scale,
                                                  term.argument
                                                  / base_term.argument)
                             for term in divisible]).square())
            if isinstance(denominator, Constant):
                break
            elif isinstance(denominator, Term):
                numerator *= Term.from_components(One, denominator.argument)
                denominator = denominator.scale * denominator.argument
                break
        return numerator * denominator.inverse()

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
        scale = self._normalizing_scale()
        return sum([(scale * term).lower_bound() for term in self.terms],
                   (scale * self.tail).lower_bound()) / scale

    def perfect_sqrt(self) -> Expression:
        terms_count = len(self.terms)
        components_discriminant = 1 + 8 * (terms_count - (not self.tail))
        has_perfect_square_structure = (
                square(sqrt_floor(components_discriminant))
                == components_discriminant)
        if not (all(isinstance(term.argument, Constant)
                    for term in self.terms)
                and (not has_perfect_square_structure or terms_count < 3)):
            raise ValueError('Unsupported value: {!r}.'.format(self))
        elif not has_perfect_square_structure:
            pass
        elif not self.tail:
            # checking if the form can be represented as
            # ``(a * sqrt(b * sqrt(x)) + c * sqrt(d * sqrt(x))) ** 2``,
            # where
            # ``a, x`` are positive rational,
            # ``b, d`` are positive non-equal rational,
            # ``c`` is non-zero rational
            max_term = max(self.terms,
                           key=abs)
            min_term = min(self.terms,
                           key=abs)
            base_argument = max_term.argument
            if not min_term.square() % base_argument:
                discriminant = ((max_term.square() - min_term.square())
                                / base_argument)
                discriminant_sqrt = discriminant.perfect_sqrt()
                if discriminant_sqrt.square() == discriminant:
                    max_scale = (max_term.scale + discriminant_sqrt) / 2
                    min_scale = (max_term.scale - discriminant_sqrt) / 2
                    one_fourth = Term(One, base_argument)
                    return (_positiveness_to_sign(min_term.is_positive())
                            * Term.from_components(One,
                                                   min_scale * one_fourth)
                            + Term.from_components(One,
                                                   max_scale * one_fourth))
        elif terms_count == 1:
            term, = self.terms
            discriminant = self.tail.square() - term.square()
            if discriminant.is_positive():
                # checking if the form can be represented as
                # ``(a * sqrt(x) + b * sqrt(y)) ** 2``,
                # where
                # ``a, b, x, y`` are rational,
                # ``x, y`` are non-equal
                discriminant_sqrt = discriminant.perfect_sqrt()
                if discriminant_sqrt.square() == discriminant:
                    return (_positiveness_to_sign(term.is_positive())
                            * Term.from_components(
                                    One, (self.tail - discriminant_sqrt) / 2)
                            + Term.from_components(
                                    One, (self.tail + discriminant_sqrt) / 2))
            else:
                # checking if the form can be represented as
                # ``(sqrt(a * sqrt(x)) + b * sqrt(c * sqrt(x))) ** 2``,
                # where
                # ``a, b, c, x`` are non-zero rational,
                # ``a, c, x`` are positive,
                # ``a, c`` are non-equal,
                # ``a * c`` is a perfect square
                discriminant /= -term.argument
                discriminant_sqrt = discriminant.perfect_sqrt()
                if discriminant_sqrt.square() == discriminant:
                    one_fourth = Term(One, term.argument)
                    return (_positiveness_to_sign(self.tail.is_positive())
                            * Term(One,
                                   (term.scale - discriminant_sqrt) / 2
                                   * one_fourth)
                            + Term(One,
                                   (term.scale + discriminant_sqrt) / 2
                                   * one_fourth))
        common_numerator, form = self.extract_common_numerator()
        common_denominator, _ = form.extract_common_denominator()
        return (Constant(common_numerator) / common_denominator).perfect_sqrt()

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
        scale = self._normalizing_scale()
        return sum([(scale * term).upper_bound()
                    for term in self.terms],
                   (scale * self.tail).upper_bound()) / scale

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

    def __str__(self) -> str:
        return (str(self.terms[0])
                + (' ' + ' '.join(map(_to_signed_value, self.terms[1:]))
                   if len(self.terms) > 1
                   else '')
                + (' ' + _to_signed_value(self.tail)
                   if self.tail
                   else ''))

    def _normalizing_scale(self) -> Rational:
        common_denominator, form = self.extract_common_denominator()
        return common_denominator * BASE ** form.significant_digits_count()


def _positiveness_to_sign(flag: bool) -> int:
    return 2 * flag - 1


def _to_signed_value(value: Union[Constant, Term]) -> str:
    return '+ ' + str(value) if value.is_positive() else '- ' + str(-value)


_T1 = TypeVar('_T1')
_T2 = TypeVar('_T2')


def _transpose(pairs_sequence: Sequence[Tuple[_T1, _T2]]
               ) -> Tuple[Sequence[_T1], Sequence[_T2]]:
    return tuple(zip(*pairs_sequence))
