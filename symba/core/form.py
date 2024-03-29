from __future__ import annotations

import math
from collections import defaultdict
from functools import reduce
from numbers import (Rational,
                     Real)
from typing import (Any,
                    Callable,
                    DefaultDict,
                    Iterable,
                    List,
                    Optional,
                    Sequence,
                    Tuple,
                    Union,
                    cast,
                    overload)

from reprit.base import generate_repr

from .constant import (ONE,
                       RAW_ZERO,
                       ZERO,
                       Constant,
                       Finite,
                       FiniteNonZero,
                       Infinite,
                       Zero,
                       to_constant,
                       try_to_constant)
from .expression import Expression
from .hints import (RawConstant,
                    RawFinite,
                    RawUnbound)
from .term import Term
from .utils import (BASE,
                    digits_count,
                    lcm,
                    positiveness_to_sign,
                    to_square_free,
                    transpose)


class Form(Expression):
    """Represents sum of square roots."""

    @classmethod
    def from_components(cls,
                        terms: List[Term],
                        tail: Union[FiniteNonZero, Zero] = ZERO) -> Expression:
        queue = sorted(terms,
                       key=abs,
                       reverse=True)
        arguments_scales: DefaultDict[
            Union[FiniteNonZero, Form, Term], Finite] = defaultdict(Zero)
        while queue:
            min_term = queue.pop()
            min_term_argument = min_term.argument
            arguments_scales[min_term_argument] += min_term.scale
            next_queue = []
            for term in queue:
                arguments_ratio = term.argument / min_term_argument
                arguments_ratio_sqrt = arguments_ratio.perfect_sqrt()
                if arguments_ratio_sqrt.square() == arguments_ratio:
                    arguments_scales[min_term_argument] += (
                            term.scale * arguments_ratio_sqrt
                    )
                else:
                    next_queue.append(term)
            queue = next_queue
        terms = [Term(scale, argument)
                 for argument, scale in arguments_scales.items()
                 if not isinstance(scale, Zero)]
        return ((cls(terms, tail) if tail or len(terms) > 1 else terms[0])
                if terms
                else tail)

    __slots__ = 'tail', 'terms'

    def __init__(self, terms: List[Term], tail: Finite = ZERO) -> None:
        self.tail, self.terms = tail, terms

    @property
    def degree(self) -> int:
        return max(term.degree for term in self.terms)

    def extract_common_denominator(self) -> Tuple[int, Form]:
        terms_common_denominators, _ = transpose(
                [term.extract_common_denominator() for term in self.terms]
        )
        tail_denominator, _ = self.tail.extract_common_denominator()
        common_denominator = reduce(lcm, terms_common_denominators,
                                    tail_denominator)
        return (common_denominator,
                self._scale(FiniteNonZero(common_denominator)))

    def extract_common_numerator(self) -> Tuple[int, Form]:
        terms_common_numerators, _ = transpose([term.extract_common_numerator()
                                                for term in self.terms])
        tail_numerator, _ = self.tail.extract_common_numerator()
        common_numerator = reduce(math.gcd, terms_common_numerators,
                                  tail_numerator)
        return common_numerator, self / common_numerator

    def inverse(self) -> Union[Finite, Form, Term]:
        common_denominator, integer_form = self.extract_common_denominator()
        numerator, denominator = (
            Factorization(tail=to_constant(common_denominator)),
            Factorization.from_form(integer_form)
        )
        while denominator.factors:
            max_factor = max(denominator.factors)
            max_factorization = denominator.factors.pop(max_factor)
            numerator = numerator.multiply(
                    denominator
                    - max_factorization.multiply_by_factor(max_factor)
            )
            denominator = (denominator.square()
                           - max_factorization.square() * max_factor.square())
        return numerator.scale_non_zero(denominator.tail.inverse()).express()

    def is_positive(self) -> bool:
        components = (*self.terms, self.tail) if self.tail else self.terms
        positive: List[Expression] = []
        negative: List[Expression] = []
        for component in components:
            (positive
             if component.is_positive()
             else negative).append(component)
        if not (positive and negative):
            return not negative
        positive_squares_sum, negative_squares_sum = (
            sum(component.square() for component in positive),
            sum(component.square() for component in negative)
        )
        assert isinstance(positive_squares_sum, Expression), (
            positive_squares_sum
        )
        assert isinstance(negative_squares_sum, Expression), (
            negative_squares_sum
        )
        return ((len(positive) * positive_squares_sum
                 - negative_squares_sum).is_positive()
                and ((positive_squares_sum
                      - len(negative) * negative_squares_sum).is_positive()
                     or self.lower_bound() >= RAW_ZERO))

    def lower_bound(self) -> RawConstant:
        common_denominator, form = self.extract_common_denominator()
        scale = BASE ** form.significant_digits_count()
        return (sum([(scale * term).lower_bound() for term in form.terms],
                    (scale * form.tail).lower_bound())
                / (common_denominator * scale))

    def perfect_sqrt(self) -> Expression:
        if self.degree != 1:
            raise ValueError('Unsupported value: {!r}.'.format(self))
        denominator, integer_form = self.extract_common_denominator()
        if not self.tail:
            arguments_gcd = form_arguments_gcd(integer_form)
            if arguments_gcd != 1:
                common_term = Term(ONE, FiniteNonZero(arguments_gcd))
                normalized_form = integer_form / common_term
                normalized_sqrt = normalized_form.perfect_sqrt()
                if normalized_sqrt.square() == normalized_form:
                    result = (Term(ONE / denominator, common_term)
                              * normalized_sqrt)
                    assert isinstance(result, Expression), result
                    return result
        elif len(self.terms) == 1:
            term, = integer_form.terms
            discriminant = integer_form.tail.square() - term.square()
            if discriminant.is_positive():
                # checking if the form can be represented as
                # ``(a * sqrt(x) + b * sqrt(y)) ** 2``,
                # where
                # ``a, b, x, y`` are rational,
                # ``x, y`` are non-equal
                discriminant_sqrt = discriminant.perfect_sqrt()
                if discriminant_sqrt.square() == discriminant:
                    scale = ONE / denominator
                    return (positiveness_to_sign(term.is_positive())
                            * Term.from_components(scale,
                                                   (integer_form.tail
                                                    - discriminant_sqrt) / 2)
                            + Term.from_components(scale,
                                                   (integer_form.tail
                                                    + discriminant_sqrt) / 2))
            else:
                # checking if the form can be represented as
                # ``((sqrt(a) + b * sqrt(c)) * sqrt(sqrt(x))) ** 2``,
                # where
                # ``a, b, c, x`` are non-zero rational,
                # ``a, c, x`` are positive,
                # ``a, c`` are non-equal,
                # ``a * c`` is a perfect square
                discriminant /= -term.argument
                discriminant_sqrt = discriminant.perfect_sqrt()
                if discriminant_sqrt.square() == discriminant:
                    scale = ONE / denominator
                    sub_term = Term(ONE, term.argument)
                    return (positiveness_to_sign(self.tail.is_positive())
                            * Term(scale,
                                   (term.scale - discriminant_sqrt) / 2
                                   * sub_term)
                            + Term(scale,
                                   (term.scale + discriminant_sqrt) / 2
                                   * sub_term))
        else:
            lesser_part, greater_part = _split_form(integer_form)
            discriminant = greater_part.square() - lesser_part.square()
            if discriminant.is_positive():
                discriminant_is_constant = not discriminant.degree
                discriminant_sqrt = (Term.from_components(ONE, discriminant)
                                     if discriminant_is_constant
                                     else discriminant.perfect_sqrt())
                if (discriminant_is_constant
                        or discriminant_sqrt.square() == discriminant):
                    addend = greater_part + discriminant_sqrt
                    if (not isinstance(addend, Form)
                            or (len(addend.terms) + bool(addend.tail)
                                < len(self.terms) + bool(self.tail))):
                        result = ((lesser_part + addend)
                                  / Term.from_components(
                                        FiniteNonZero(denominator), 2 * addend
                                ))
                        assert isinstance(result, Expression), result
                        return result
        common_denominator, integer_form = self.extract_common_denominator()
        common_numerator, _ = integer_form.extract_common_numerator()
        return (
                FiniteNonZero(common_numerator) / common_denominator
        ).perfect_sqrt()

    def significant_digits_count(self) -> int:
        return (max(max(term.significant_digits_count()
                        for term in self.terms),
                    self.tail.significant_digits_count())
                + digits_count(len(self.terms) + bool(self.tail)) + 1)

    def square(self) -> Expression:
        terms = ([]
                 if isinstance(self.tail, Zero)
                 else [(2 * self.tail) * term for term in self.terms])
        tail = (self.tail.square()
                + _sift_components([2 * (self.terms[step] * self.terms[index])
                                    for step in range(1, len(self.terms))
                                    for index in range(step)]
                                   + [term.square() for term in self.terms],
                                   terms))
        return Form.from_components(terms, tail)

    def upper_bound(self) -> RawConstant:
        common_denominator, form = self.extract_common_denominator()
        scale = BASE ** form.significant_digits_count()
        return (sum([(scale * term).upper_bound() for term in form.terms],
                    (scale * form.tail).upper_bound())
                / (common_denominator * scale))

    @overload
    def __add__(self, other: RawFinite) -> Union[Form, Term]:
        ...

    @overload
    def __add__(self, other: RawUnbound) -> Union[Form, Infinite, Term]:
        ...

    @overload
    def __add__(self, other: FiniteNonZero) -> Union[Form, Term]:
        ...

    @overload
    def __add__(self, other: Infinite) -> Infinite:
        ...

    @overload
    def __add__(self, other: Zero) -> Form:
        ...

    @overload
    def __add__(self, other: Form) -> Union[Finite, Form, Term]:
        ...

    @overload
    def __add__(self, other: Any) -> Any:
        ...

    def __add__(self, other: Any) -> Any:
        other = try_to_constant(other)
        return (self._add_constant(other)
                if isinstance(other, (FiniteNonZero, Infinite, Zero))
                else (self._add_term(other)
                      if isinstance(other, Term)
                      else (Form.from_components(self.terms + other.terms,
                                                 self.tail + other.tail)
                            if isinstance(other, Form)
                            else NotImplemented)))

    @overload
    def __eq__(self, other: Union[RawConstant, Expression]) -> bool:
        ...

    @overload
    def __eq__(self, other: Any) -> Any:
        ...

    def __eq__(self, other: Any) -> Any:
        return (self is other
                or (self.tail == other.tail
                    and len(self.terms) == len(other.terms)
                    and set(self.terms) == set(other.terms))
                if isinstance(other, Form)
                else (False
                      if isinstance(other, (Expression, Rational, Real))
                      else NotImplemented))

    def __hash__(self) -> int:
        return hash((frozenset(self.terms), self.tail))

    @overload
    def __mul__(self, other: RawFinite) -> Union[Form, Zero]:
        ...

    @overload
    def __mul__(self, other: RawUnbound) -> Union[Form, Infinite, Zero]:
        ...

    @overload
    def __mul__(self, other: Union[FiniteNonZero, Term]) -> Form:
        ...

    @overload
    def __mul__(self, other: Infinite) -> Infinite:
        ...

    @overload
    def __mul__(self, other: Zero) -> Zero:
        ...

    @overload
    def __mul__(self, other: Form) -> Union[FiniteNonZero, Form]:
        ...

    @overload
    def __mul__(self, other: Expression) -> Expression:
        ...

    @overload
    def __mul__(self, other: Any) -> Any:
        ...

    def __mul__(self, other: Any) -> Any:
        other = try_to_constant(other)
        return (self._multiply_by_constant(other)
                if isinstance(other, Constant)
                else (self._multiply_by_term(other)
                      if isinstance(other, Term)
                      else (self._multiply_by_form(other)
                            if isinstance(other, Form)
                            else NotImplemented)))

    def __neg__(self) -> Form:
        return Form([-term for term in self.terms],
                    tail=-self.tail)

    @overload
    def __radd__(self, other: Union[RawConstant, Expression]) -> Expression:
        ...

    @overload
    def __radd__(self, other: Any) -> Any:
        ...

    def __radd__(self, other: Any) -> Any:
        other = try_to_constant(other)
        return (self._add_constant(other)
                if isinstance(other, (FiniteNonZero, Infinite, Zero))
                else (self._add_term(other)
                      if isinstance(other, Term)
                      else NotImplemented))

    __repr__ = generate_repr(__init__)

    @overload
    def __rmul__(self, other: RawFinite) -> Union[Form, Zero]:
        ...

    @overload
    def __rmul__(self, other: RawUnbound) -> Union[Form, Infinite, Zero]:
        ...

    @overload
    def __rmul__(self, other: FiniteNonZero) -> Form:
        ...

    @overload
    def __rmul__(self, other: Term) -> Form:
        ...

    @overload
    def __rmul__(self, other: Infinite) -> Infinite:
        ...

    @overload
    def __rmul__(self, other: Zero) -> Zero:
        ...

    @overload
    def __rmul__(self, other: Expression) -> Expression:
        ...

    @overload
    def __rmul__(self, other: Any) -> Any:
        ...

    def __rmul__(self, other: Any) -> Any:
        other = try_to_constant(other)
        return (self._multiply_by_constant(other)
                if isinstance(other, Constant)
                else (self._multiply_by_term(other)
                      if isinstance(other, Term)
                      else NotImplemented))

    def __str__(self) -> str:
        return (str(self.terms[0])
                + (' ' + ' '.join(map(_to_signed_value, self.terms[1:]))
                   if len(self.terms) > 1
                   else '')
                + (''
                   if isinstance(self.tail, Zero)
                   else ' ' + _to_signed_value(self.tail)))

    def _add_constant(self, other: Union[Finite, Infinite]) -> Expression:
        tail = self.tail + other
        return (tail
                if isinstance(tail, Infinite)
                else (Form(self.terms, tail)
                      if tail or len(self.terms) > 1
                      else self.terms[0]))

    def _add_term(self, other: Term) -> Expression:
        return Form.from_components(self.terms + [other], self.tail)

    def _multiply_by_constant(self, other: Constant) -> Expression:
        return (self._scale(other)
                if isinstance(other, FiniteNonZero)
                else ((other if self.is_positive() else -other)
                      if isinstance(other, Infinite)
                      else other))

    def _multiply_by_form(self, other: Form) -> Expression:
        if self == other:
            return self.square()
        tail, other_tail = self.tail, other.tail
        terms = (([]
                  if isinstance(other_tail, Zero)
                  else [term * other_tail for term in self.terms])
                 + ([]
                    if isinstance(tail, Zero)
                    else [other_term * tail for other_term in other.terms]))
        tail = (tail * other_tail
                + _sift_components([term * other_term
                                    for term in self.terms
                                    for other_term in other.terms],
                                   terms))
        return Form.from_components(terms, tail)

    def _multiply_by_term(self, other: Term) -> Expression:
        terms = [] if isinstance(self.tail, Zero) else [other * self.tail]
        return Form(terms,
                    _sift_components([term * other for term in self.terms],
                                     terms))

    def _scale(self, other: FiniteNonZero) -> Form:
        return (self
                if other == ONE
                else Form([term * other for term in self.terms],
                          self.tail * other))


def form_arguments_gcd(integer_form: Form) -> int:
    result, _, coprime_indices = _split_integers_by_gcd(
            [_evaluate_integer_term_argument(term)
             for term in sorted(integer_form.terms,
                                key=_term_key)]
    )
    return 1 if coprime_indices else result


def _split_form(integer_form: Form) -> Tuple[Form, Form]:
    terms: Sequence[Term] = integer_form.terms
    if len(terms) == 3:
        first_term, *rest_terms = terms
        return Form(rest_terms), Form([first_term], integer_form.tail)
    surds, terms = zip(*sorted([(_integer_term_to_surd(term), term)
                                for term in terms]))
    cocomposite_indices, coprime_indices = _split_integers(surds)
    return ((Form([terms[index] for index in cocomposite_indices]),
             Form([terms[index] for index in coprime_indices],
                  integer_form.tail)))


def _integer_term_to_surd(term: Term) -> int:
    return to_square_free(_evaluate_integer_term_argument(term))


def _evaluate_integer_term_argument(term: Term) -> int:
    argument = term.argument
    assert isinstance(argument, FiniteNonZero), argument
    return argument.raw.numerator


def _split_integers(values: Sequence[int]) -> Tuple[List[int], List[int]]:
    gcd, cocomposite_indices, coprime_indices = _split_integers_by_gcd(values)
    if not coprime_indices:
        _, cocomposite_indices, coprime_indices = _split_integers_by_gcd(
                value // gcd for value in values
        )
    return cocomposite_indices, coprime_indices


def _split_integers_by_gcd(
        integers: Iterable[int]
) -> Tuple[int, List[int], List[int]]:
    iterator = iter(integers)
    gcd = next(iterator)
    cocomposite_indices, coprime_indices, gcd, start = (
        ([1], [0], next(iterator), 2) if gcd == 1 else ([0], [], gcd, 1)
    )
    for index, value in enumerate(iterator,
                                  start=start):
        value_gcd = math.gcd(gcd, value)
        if value_gcd == 1:
            coprime_indices.append(index)
        else:
            gcd = value_gcd
            cocomposite_indices.append(index)
    return gcd, cocomposite_indices, coprime_indices


class Factor:
    def express(self) -> Term:
        return self._term

    def square(self) -> Expression:
        return self._term.argument

    argument: Union[FiniteNonZero, Form, Term]
    degree: int
    _term: Term

    __slots__ = 'argument', 'degree', '_term'

    def __init__(self,
                 argument: Union[FiniteNonZero, Form, Term],
                 degree: int) -> None:
        self.argument, self.degree = argument, degree
        term = argument
        for _ in range(degree):
            term = Term(ONE, term)
        assert isinstance(term, Term)
        self._term = term

    @overload
    def __eq__(self, other: 'Factor') -> bool:
        ...

    @overload
    def __eq__(self, other: Any) -> Any:
        ...

    def __eq__(self, other: 'Factor') -> bool:
        return (self.degree == other.degree and self.argument == other.argument
                if isinstance(other, Factor)
                else NotImplemented)

    def __hash__(self) -> int:
        return hash((self.argument, self.degree))

    def __lt__(self, other: 'Factor') -> bool:
        return ((self.express().degree, self.express().argument)
                < (other.express().degree, other.express().argument))

    __repr__ = generate_repr(__init__)

    def __str__(self) -> str:
        return str(self.express())


class Factorization:
    @classmethod
    def from_factor(cls, factor: Factor) -> Factorization:
        result = cls()
        result.factors[factor].tail = ONE
        return result

    @classmethod
    def from_form(cls, form: Form) -> Factorization:
        result = cls(tail=form.tail)
        factors = result.factors
        for term in form.terms:
            _populate_factors(factors, term)
        return result

    @classmethod
    def from_term(cls, term: Term) -> Factorization:
        result = cls()
        _populate_factors(result.factors, term)
        return result

    __slots__ = 'factors', 'tail'

    def __init__(self,
                 factors: Optional[DefaultDict[Factor, Factorization]]
                 = None,
                 tail: Union[FiniteNonZero, Zero] = ZERO) -> None:
        self.factors, self.tail = (defaultdict(Factorization)
                                   if factors is None
                                   else factors,
                                   tail)

    def express(self) -> Union[Finite, Form, Term]:
        return sum([factor.express() * factorization.express()
                    for factor, factorization in self.factors.items()],
                   self.tail)

    def multiply(self: Factorization, other: Factorization) -> Factorization:
        factors, tail = self.factors, self.tail
        other_factors, other_tail = other.factors, other.tail
        result = self.scale(other.tail) + other.scale(self.tail)
        result.tail /= 2
        for factor, factorization in factors.items():
            for other_factor, other_factorization in other_factors.items():
                result_factorization = (
                    factorization.multiply(other_factorization)
                )
                if factor == other_factor:
                    squared_factor = factor.square()
                    assert isinstance(squared_factor,
                                      (FiniteNonZero, Form, Term)), (
                        squared_factor
                    )
                    result += (
                        result_factorization.scale_non_zero(squared_factor)
                        if isinstance(squared_factor, FiniteNonZero)
                        else (result_factorization
                              .multiply_by_form(squared_factor)
                              if isinstance(squared_factor, Form)
                              else (result_factorization
                                    .multiply_by_term(squared_factor)))
                    )
                else:
                    max_factor, min_factor = ((other_factor, factor)
                                              if factor < other_factor
                                              else (factor, other_factor))
                    result.factors[max_factor] += (
                        result_factorization.multiply_by_factor(min_factor))
        return result

    def multiply_by_factor(self, factor: Factor) -> Factorization:
        return self.multiply(Factorization.from_factor(factor))

    def multiply_by_form(self, form: Form) -> Factorization:
        return sum([self.multiply_by_term(term) for term in form.terms],
                   self.scale(form.tail))

    def multiply_by_term(self, term: Term) -> Factorization:
        return self.multiply(Factorization.from_term(term))

    def scale(self, scale: Union[FiniteNonZero, Zero]) -> Factorization:
        return (Factorization()
                if isinstance(scale, Zero)
                else self.scale_non_zero(scale))

    def scale_non_zero(self, scale: FiniteNonZero) -> Factorization:
        result = Factorization(tail=self.tail * scale)
        factors = result.factors
        for factor, factorization in self.factors.items():
            factors[factor] = factorization.scale_non_zero(scale)
        return result

    def square(self, _two: FiniteNonZero = FiniteNonZero(2)) -> Factorization:
        result = self.scale(_two * self.tail)
        result.tail /= 2
        factorizations = tuple(self.factors.items())
        for offset, (factor, factorization) in enumerate(factorizations,
                                                         start=1):
            result += factorization.square() * factor.square()
            for next_index in range(offset, len(factorizations)):
                next_factor, next_factorization = factorizations[next_index]
                max_factor, min_factor = ((next_factor, factor)
                                          if factor < next_factor
                                          else (factor, next_factor))
                result.factors[max_factor] += (factorization
                                               .scale_non_zero(_two)
                                               .multiply_by_factor(min_factor)
                                               .multiply(next_factorization))
        return result

    def __add__(self, other: Factorization) -> Factorization:
        if not (self and other):
            return self or other
        factors, rest_factors = ((other.factors.copy(), self.factors)
                                 if len(self.factors) < len(other.factors)
                                 else (self.factors.copy(), other.factors))
        for factor, factorization in rest_factors.items():
            factors[factor] += factorization
        return Factorization(factors, self.tail + other.tail)

    def __bool__(self) -> bool:
        return bool(self.tail or any(self.factors.values()))

    def __iadd__(self, other: Factorization) -> Factorization:
        if not self:
            self.factors, self.tail = other.factors.copy(), other.tail
        elif other:
            factors, rest_factors = ((other.factors.copy(), self.factors)
                                     if len(self.factors) < len(other.factors)
                                     else (self.factors, other.factors))
            for factor, factorization in rest_factors.items():
                factors[factor] += factorization
            self.factors = factors
            self.tail += other.tail
        return self

    def __len__(self) -> int:
        return bool(self.tail) + sum(map(len, self.factors.values()))

    @overload
    def __mul__(self, other: Expression) -> Factorization:
        ...

    @overload
    def __mul__(self, other: Any) -> Any:
        ...

    def __mul__(self, other: Any) -> Any:
        return (self.scale(other)
                if isinstance(other, FiniteNonZero)
                else (self.multiply_by_term(other)
                      if isinstance(other, Term)
                      else (self.multiply_by_form(other)
                            if isinstance(other, Form)
                            else NotImplemented)))

    def __neg__(self) -> Factorization:
        result = Factorization(tail=-self.tail)
        factors = result.factors
        for factor, factorization in self.factors.items():
            factors[factor] = -factorization
        return result

    __repr__ = generate_repr(__init__)

    __rmul__ = __mul__

    def __str__(self) -> str:
        head = ' + '.join([
            '{} * {}'.format(
                    factor,
                    cast(
                            Callable[[Factorization], str],
                            (str
                             if (len(factorization) == 1
                                 and (factorization.tail >= 0
                                      and
                                      all(sub_factorization.tail >= 0
                                          for sub_factorization
                                          in factorization.factors.values())))
                             else '({})'.format)
                    )(factorization)
            )
            for factor, factorization in self.factors.items()
            if factorization
        ])
        return ((head + (' + ' + str(self.tail) if self.tail else ''))
                if head
                else str(self.tail))

    def __sub__(self, other: Factorization) -> Factorization:
        return self + (-other)


def _factor_term(term: Term) -> Iterable[Factor]:
    queue: List[Tuple[int, Term]] = [(0, term)]
    while queue:
        degree, step = queue.pop()
        if degree and step.scale != 1:
            yield Factor(step.scale, degree)
        argument = step.argument
        if isinstance(argument, Term):
            queue.append((degree + 1, argument))
        elif isinstance(argument, Form):
            common_denominator, argument = (argument
                                            .extract_common_denominator())
            common_numerator, argument = argument.extract_common_numerator()
            if not (common_numerator == 1 == common_denominator):
                yield Factor(
                        FiniteNonZero(common_numerator) / common_denominator,
                        degree + 1
                )
            yield Factor(argument, degree + 1)
        else:
            yield Factor(argument, degree + 1)


def _populate_factors(children: DefaultDict[Factor, Factorization],
                      term: Term) -> None:
    *rest_factors, first_factor = _factor_term(term)
    last_factorization = children[first_factor]
    for factor in rest_factors:
        last_factorization = last_factorization.factors[factor]
    last_factorization.tail += term.scale


def _sift_components(components: Iterable[Expression],
                     terms: List[Term]) -> Finite:
    tail: Finite = ZERO
    for component in components:
        if isinstance(component, Term):
            terms.append(component)
        elif isinstance(component, Form):
            tail += component.tail
            terms.extend(component.terms)
        else:
            assert isinstance(component, FiniteNonZero), component
            tail += component
    return tail


def _term_key(term: Term) -> Tuple[int, Expression]:
    return term.degree, term.argument


def _to_signed_value(value: Union[FiniteNonZero, Term]) -> str:
    return '+ ' + str(value) if value.is_positive() else '- ' + str(-value)
