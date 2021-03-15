import math
from collections import defaultdict
from functools import reduce
from numbers import (Rational,
                     Real)
from typing import (Any,
                    DefaultDict,
                    Dict,
                    Iterable,
                    List,
                    Optional,
                    Tuple,
                    Union)

from reprit.base import generate_repr

from .abcs import Expression
from .constant import (Constant,
                       One,
                       Zero)
from .hints import SqrtEvaluator
from .term import Term
from .utils import (BASE,
                    digits_count,
                    lcm,
                    positiveness_to_sign,
                    sqrt_floor,
                    square,
                    transpose)


class Form(Expression):
    """Represents sum of square roots."""

    @classmethod
    def from_components(cls,
                        terms: List[Term],
                        tail: Constant = Zero) -> Expression:
        arguments_scales = (defaultdict
                            (Constant))  # type: Dict[Expression, Constant]
        queue = sorted(terms,
                       key=_term_key,
                       reverse=True)
        while queue:
            min_term = queue.pop()
            min_term_argument = min_term.argument
            arguments_scales[min_term_argument] += min_term.scale
            next_queue, min_term_argument_type = [], type(min_term_argument)
            for term in queue:
                if isinstance(term.argument, min_term_argument_type):
                    ratio = term.argument / min_term_argument
                    if isinstance(ratio, Constant):
                        ratio_sqrt = ratio.perfect_sqrt()
                        if ratio_sqrt.square() == ratio:
                            arguments_scales[min_term_argument] += (
                                    term.scale * ratio_sqrt)
                            continue
                next_queue.append(term)
            queue = next_queue
        terms = [Term(scale, argument)
                 for argument, scale in arguments_scales.items()
                 if scale]
        return ((cls(terms,
                     tail=tail)
                 if tail or len(terms) > 1
                 else terms[0])
                if terms
                else tail)

    __slots__ = 'tail', 'terms'

    def __init__(self, terms: List[Term], tail: Constant = Zero) -> None:
        self.tail, self.terms = tail, terms

    @property
    def degree(self) -> int:
        return max(term.degree for term in self.terms)

    def evaluate(self, sqrt_evaluator: Optional[SqrtEvaluator] = None) -> Real:
        return sum([term.evaluate(sqrt_evaluator) for term in self.terms],
                   self.tail.evaluate(sqrt_evaluator))

    def extract_common_denominator(self) -> Tuple[int, 'Form']:
        terms_common_denominators, _ = transpose(
                [term.extract_common_denominator() for term in self.terms])
        tail_denominator, _ = self.tail.extract_common_denominator()
        common_denominator = reduce(lcm, terms_common_denominators,
                                    tail_denominator)
        return common_denominator, self * common_denominator

    def extract_common_numerator(self) -> Tuple[int, 'Form']:
        terms_common_numerators, _ = transpose(
                [term.extract_common_numerator() for term in self.terms])
        tail_numerator, _ = self.tail.extract_common_numerator()
        common_numerator = reduce(math.gcd, terms_common_numerators,
                                  tail_numerator)
        return common_numerator, self / common_numerator

    def inverse(self) -> Expression:
        common_denominator, form = self.extract_common_denominator()
        numerator, factorization = (
            Factorization(tail=One * common_denominator),
            Factorization.from_form(form))
        while factorization.children:
            max_term = max(factorization.children,
                           key=_term_key)
            max_term_factorization = factorization.children.pop(max_term)
            numerator = numerator.multiply(
                    factorization + (-max_term) * max_term_factorization)
            factorization = (
                    factorization.square()
                    + (-max_term.square()) * max_term_factorization.square())
        return numerator.express() * factorization.tail.inverse()

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
        return self.lower_bound() >= 0

    def lower_bound(self) -> Rational:
        common_denominator, form = self.extract_common_denominator()
        scale = BASE ** form.significant_digits_count()
        return (sum([(scale * term).lower_bound() for term in form.terms],
                    (scale * form.tail).lower_bound())
                / (common_denominator * scale))

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
                    return (positiveness_to_sign(min_term.is_positive())
                            * Term.from_components(One, min_scale * one_fourth)
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
                    return (positiveness_to_sign(term.is_positive())
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
                    return (positiveness_to_sign(self.tail.is_positive())
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
        return (max(max(term.significant_digits_count()
                        for term in self.terms),
                    self.tail.significant_digits_count())
                + digits_count(len(self.terms) + bool(self.tail)))

    def square(self) -> Expression:
        terms = ([(2 * self.tail) * term for term in self.terms]
                 if self.tail
                 else [])
        tail = (self.tail.square()
                + _sift_components([2 * (self.terms[step] * self.terms[index])
                                    for step in range(1, len(self.terms))
                                    for index in range(step)]
                                   + [term.square() for term in self.terms],
                                   terms))
        return Form.from_components(terms, tail)

    def upper_bound(self) -> Rational:
        common_denominator, form = self.extract_common_denominator()
        scale = BASE ** form.significant_digits_count()
        return (sum([(scale * term).upper_bound() for term in form.terms],
                    (scale * form.tail).upper_bound())
                / (common_denominator * scale))

    def __add__(self, other: Union[Real, Expression]) -> Expression:
        return (self._add_constant(other)
                if isinstance(other, (Real, Constant))
                else (self._add_term(other)
                      if isinstance(other, Term)
                      else (Form.from_components(self.terms + other.terms,
                                                 self.tail + other.tail)
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
        return (self._multiply_by_constant(other)
                if isinstance(other, (Real, Constant))
                else (self._multiply_by_term(other)
                      if isinstance(other, Term)
                      else (self._multiply_by_form(other)
                            if isinstance(other, Form)
                            else NotImplemented)))

    def __neg__(self) -> 'Form':
        return Form([-term for term in self.terms],
                    tail=-self.tail)

    def __radd__(self, other: Union[Real, Expression]) -> Expression:
        return (self._add_constant(other)
                if isinstance(other, (Real, Constant))
                else (self._add_term(other)
                      if isinstance(other, Term)
                      else NotImplemented))

    __repr__ = generate_repr(__init__)

    def __rmul__(self, other: Union[Real, Expression]) -> Expression:
        return (self._multiply_by_constant(other)
                if isinstance(other, (Real, Constant))
                else (self._multiply_by_term(other)
                      if isinstance(other, Term)
                      else NotImplemented))

    def __str__(self) -> str:
        return (str(self.terms[0])
                + (' ' + ' '.join(map(_to_signed_value, self.terms[1:]))
                   if len(self.terms) > 1
                   else '')
                + (' ' + _to_signed_value(self.tail)
                   if self.tail
                   else ''))

    def _add_constant(self, other: Constant) -> 'Form':
        tail = self.tail + other
        return (Form(self.terms, tail)
                if tail or len(self.terms) > 1
                else self.terms[0])

    def _add_term(self, other: Term) -> Expression:
        return Form.from_components(self.terms + [other], self.tail)

    def _multiply_by_constant(self,
                              other: Union[Real, Constant]) -> Expression:
        return ((self
                 if other == One
                 else Form([term * other for term in self.terms],
                           tail=self.tail * other))
                if other
                else Zero)

    def _multiply_by_form(self, other: 'Form') -> Expression:
        if self == other:
            return self.square()
        tail, other_tail = self.tail, other.tail
        terms = (([term * other_tail for term in self.terms]
                  if other_tail
                  else [])
                 + ([other_term * tail for other_term in other.terms]
                    if tail
                    else []))
        tail = (tail * other_tail
                + _sift_components([term * other_term
                                    for term in self.terms
                                    for other_term in other.terms],
                                   terms))
        return Form.from_components(terms, tail)

    def _multiply_by_term(self, other: Term) -> Expression:
        terms = ([other * self.tail]
                 if self.tail
                 else [])
        return Form(terms, _sift_components([term * other
                                             for term in self.terms],
                                            terms))


class Factorization:
    @classmethod
    def from_form(cls, form: Form) -> 'Factorization':
        result = cls(tail=form.tail)
        children = result.children
        for term in form.terms:
            _populate_children(children, term)
        return result

    @classmethod
    def from_term(cls, term: Term) -> 'Factorization':
        result = cls()
        _populate_children(result.children, term)
        return result

    __slots__ = 'children', 'tail'

    def __init__(self,
                 children
                 : Optional[DefaultDict[Term, 'Factorization']] = None,
                 tail: Constant = Zero) -> None:
        self.children, self.tail = (defaultdict(Factorization)
                                    if children is None
                                    else children,
                                    tail)

    def express(self) -> Expression:
        return sum([child * child_factorization.express()
                    for child, child_factorization in self.children.items()],
                   self.tail)

    def square(self) -> 'Factorization':
        return self.multiply(self)

    def __add__(self, other: 'Factorization') -> 'Factorization':
        if not (self and other):
            return self or other
        children = self.children.copy()
        for child, child_factorization in other.children.items():
            children[child] += child_factorization
        return Factorization(children, self.tail + other.tail)

    def __bool__(self) -> bool:
        return bool(self.tail or any(self.children.values()))

    def __len__(self) -> int:
        return bool(self.tail) + sum(map(len, self.children.values()))

    def __mul__(self, other: Expression) -> 'Factorization':
        return (self.scale(other)
                if isinstance(other, Constant)
                else (self.multiply_by_term(other)
                      if isinstance(other, Term)
                      else (self.multiply_by_form(other)
                            if isinstance(other, Form)
                            else NotImplemented)))

    __rmul__ = __mul__

    def __str__(self) -> str:
        head = ' + '.join([
            '{} * {}'.format(child,
                             (str
                              if len(child_factorization) == 1
                              else '({})'.format)
                             (child_factorization))
            for child, child_factorization in self.children.items()
            if child_factorization])
        return ((head + (' + ' + str(self.tail) if self.tail else ''))
                if head
                else str(self.tail))

    def multiply(self: 'Factorization',
                 other: 'Factorization') -> 'Factorization':
        children, tail = self.children, self.tail
        other_children, other_tail = other.children, other.tail
        result = self.scale(other.tail) + other.scale(self.tail)
        result.tail /= 2
        for left_term, left_factorization in children.items():
            for right_term, right_factorization in other_children.items():
                child_factorization = (left_factorization
                                       .multiply(right_factorization))
                if left_term == right_term:
                    squared_term = left_term.square()
                    if isinstance(squared_term, Constant):
                        result += child_factorization.scale(squared_term)
                    elif isinstance(squared_term, Form):
                        result += (child_factorization
                                   .multiply_by_form(squared_term))
                    else:
                        assert isinstance(squared_term, Term)
                        result += (child_factorization
                                   .multiply_by_term(squared_term))
                else:
                    max_term, min_term = (max(left_term, right_term,
                                              key=_term_key),
                                          min(left_term, right_term,
                                              key=_term_key))
                    scaleless_max_term = Term(One, max_term.argument)
                    result.children[scaleless_max_term] += (
                        (child_factorization.multiply_by_term(min_term)
                         .scale(max_term.scale)))
        return result

    def multiply_by_form(self, form: Form) -> 'Factorization':
        return sum([self.multiply_by_term(term) for term in form.terms],
                   self.scale(form.tail))

    def multiply_by_term(self, term: Term) -> 'Factorization':
        return self.multiply(Factorization.from_term(term))

    def scale(self, scale: Constant) -> 'Factorization':
        return self._scale(scale) if scale else Factorization()

    def _scale(self, scale: Constant) -> 'Factorization':
        result = Factorization(tail=self.tail * scale)
        children = result.children
        for child, child_factorization in self.children.items():
            children[child] = child_factorization._scale(scale)
        return result


def _sift_components(components: Iterable[Expression],
                     terms: List[Term]) -> Constant:
    tail = Zero
    for component in components:
        if isinstance(component, Term):
            terms.append(component)
        elif isinstance(component, Form):
            tail += component.tail
            terms.extend(component.terms)
        else:
            tail += component
    return tail


def _atomize_term(term: Term) -> Iterable[Expression]:
    queue = [(0, term)]
    while queue:
        degree, step = queue.pop()
        yield _to_graded_term(step.scale, degree)
        argument = step.argument
        if isinstance(argument, Term):
            queue.append((degree + 1, argument))
        elif isinstance(argument, Form):
            common_numerator, argument = argument.extract_common_numerator()
            if common_numerator != 1:
                yield _to_graded_term(Constant(common_numerator), degree + 1)
            yield _to_graded_term(argument, degree + 1)
        else:
            yield _to_graded_term(argument, degree + 1)


def _populate_children(children: DefaultDict[Term, Factorization],
                       term: Term) -> None:
    scale, *successors, scaleless_term = _atomize_term(term)
    last_children = children[scaleless_term]
    for successor in successors:
        last_children = last_children.children[successor]
    last_children.tail += term.scale


def _term_key(term: Term) -> Tuple[int, Expression]:
    return term.degree, term.argument


def _to_graded_term(argument: Expression, degree: int) -> Expression:
    result = argument
    for _ in range(degree):
        result = Term(One, result)
    return result


def _to_signed_value(value: Union[Constant, Term]) -> str:
    return '+ ' + str(value) if value.is_positive() else '- ' + str(-value)
