from __future__ import annotations

import math
from typing import (TYPE_CHECKING,
                    Any,
                    Tuple,
                    Union,
                    overload)

from reprit.base import generate_repr

from .constant import (ONE,
                       ZERO,
                       Constant,
                       FiniteNonZero,
                       Infinite,
                       Zero,
                       to_constant,
                       try_to_constant)
from .expression import Expression
from .hints import (RawConstant,
                    RawFinite,
                    RawUnbound)
from .utils import (ceil_half,
                    rational_sqrt_lower_bound,
                    rational_sqrt_upper_bound)

if TYPE_CHECKING:
    from .form import Form


class Term(Expression):
    """Represents square root of the expression."""

    @classmethod
    def from_components(cls,
                        scale: FiniteNonZero,
                        argument: Expression) -> Expression:
        if not (scale and argument):
            return ZERO
        denominator, argument = argument.extract_common_denominator()
        scale /= denominator
        argument *= denominator
        argument_perfect_sqrt = argument.perfect_sqrt()
        argument_perfect_part = argument_perfect_sqrt.square()
        result = (argument_perfect_sqrt * scale
                  if argument == argument_perfect_part
                  else (argument_perfect_sqrt
                        * cls(scale, argument / argument_perfect_part)))
        assert isinstance(result, Expression), result
        return result

    __slots__ = 'argument', 'scale'

    def __init__(self,
                 scale: FiniteNonZero,
                 argument: Expression) -> None:
        from .form import Form
        assert isinstance(argument, (FiniteNonZero, Form, Term)), argument
        self.argument, self.scale = argument, scale

    @property
    def degree(self) -> int:
        return self.argument.degree + 1

    def extract_common_denominator(self) -> Tuple[int, Term]:
        common_denominator, scale = self.scale.extract_common_denominator()
        return common_denominator, Term(scale, self.argument)

    def extract_common_numerator(self) -> Tuple[int, Term]:
        common_numerator, scale = self.scale.extract_common_numerator()
        return common_numerator, Term(scale, self.argument)

    def inverse(self) -> Term:
        scale = self.scale.inverse()
        argument: Expression
        denominator, argument = (
            self.argument.inverse().extract_common_denominator()
        )
        scale /= denominator
        argument *= denominator
        return Term(scale, argument)

    def is_positive(self) -> bool:
        return self.scale.is_positive()

    def lower_bound(self) -> RawConstant:
        return (rational_sqrt_lower_bound(self.square().lower_bound())
                if self.is_positive()
                else -(-self).upper_bound())

    def perfect_sqrt(self) -> Expression:
        return self.scale.perfect_sqrt()

    def significant_digits_count(self) -> int:
        return ceil_half(self.square().significant_digits_count())

    def square(self) -> Expression:
        return self.scale.square() * self.argument

    def upper_bound(self) -> RawConstant:
        return (rational_sqrt_upper_bound(self.square().upper_bound())
                if self.is_positive()
                else -(-self).lower_bound())

    @overload
    def __add__(self, other: RawFinite) -> Union[Form, Term]:
        ...

    @overload
    def __add__(self, other: RawUnbound) -> Union[Infinite, Form, Term]:
        ...

    @overload
    def __add__(self, other: FiniteNonZero) -> Form:
        ...

    @overload
    def __add__(self, other: Infinite) -> Infinite:
        ...

    @overload
    def __add__(self, other: Zero) -> Term:
        ...

    @overload
    def __add__(self, other: Any) -> Any:
        ...

    def __add__(self, other: Any) -> Any:
        from .form import Form
        other = try_to_constant(other)
        return (self._add_constant(other)
                if isinstance(other, Constant)
                else (Form.from_components([self, other])
                      if isinstance(other, Term)
                      else NotImplemented))

    @overload
    def __eq__(self, other: Expression) -> bool:
        ...

    @overload
    def __eq__(self, other: Any) -> Any:
        ...

    def __eq__(self, other: Any) -> Any:
        return (isinstance(other, Term)
                and self.is_positive() is other.is_positive()
                and self.square() == other.square()
                if isinstance(other, Expression)
                else NotImplemented)

    @overload
    def __ge__(self, other: Union[RawConstant, Expression]) -> bool:
        ...

    @overload
    def __ge__(self, other: Any) -> Any:
        ...

    def __ge__(self, other: Any) -> Any:
        other = try_to_constant(other)
        return ((other <= self
                 if isinstance(other, Infinite)
                 else (not other.is_positive()
                       or other.square() <= self.square()
                       if self.is_positive()
                       else (not other.is_positive()
                             and other.square() >= self.square())))
                if isinstance(other, Expression)
                else NotImplemented)

    @overload
    def __gt__(self, other: Union[RawConstant, Expression]) -> bool:
        ...

    @overload
    def __gt__(self, other: Any) -> Any:
        ...

    def __gt__(self, other: Any) -> Any:
        other = try_to_constant(other)
        return ((other < self
                 if isinstance(other, Infinite)
                 else ((not other.is_positive()
                        or other.square() < self.square())
                       if self.is_positive()
                       else (not other.is_positive()
                             and other.square() > self.square())))
                if isinstance(other, Expression)
                else NotImplemented)

    def __hash__(self) -> int:
        return hash((self.is_positive(), self.square()))

    @overload
    def __le__(self, other: Union[RawConstant, Expression]) -> bool:
        ...

    @overload
    def __le__(self, other: Any) -> Any:
        ...

    def __le__(self, other: Any) -> Any:
        other = try_to_constant(other)
        return ((other >= self
                 if isinstance(other, Infinite)
                 else ((other.is_positive()
                        and other.square() >= self.square())
                       if self.is_positive()
                       else (other.is_positive()
                             or other.square() <= self.square())))
                if isinstance(other, Expression)
                else NotImplemented)

    @overload
    def __lt__(self, other: Union[RawConstant, Expression]) -> bool:
        ...

    @overload
    def __lt__(self, other: Any) -> Any:
        ...

    def __lt__(self, other: Any) -> Any:
        other = try_to_constant(other)
        return ((other > self
                 if isinstance(other, Infinite)
                 else ((other.is_positive() and other.square() > self.square())
                       if self.is_positive()
                       else (other.is_positive()
                             or other.square() < self.square())))
                if isinstance(other, Expression)
                else NotImplemented)

    @overload
    def __mul__(self, other: FiniteNonZero) -> Term:
        ...

    @overload
    def __mul__(self, other: Infinite) -> Infinite:
        ...

    @overload
    def __mul__(self, other: RawFinite) -> Union[Term, Zero]:
        ...

    @overload
    def __mul__(self, other: RawUnbound) -> Union[Infinite, Term, Zero]:
        ...

    @overload
    def __mul__(self, other: Term) -> Union[FiniteNonZero, Form, Term]:
        ...

    @overload
    def __mul__(self, other: Zero) -> Zero:
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
                      else NotImplemented))

    def __neg__(self) -> Term:
        return Term(-self.scale, self.argument)

    @overload
    def __radd__(self, other: Union[RawConstant, Expression]) -> Expression:
        ...

    @overload
    def __radd__(self, other: Any) -> Any:
        ...

    def __radd__(self, other: Any) -> Any:
        other = try_to_constant(other)
        return (self._add_constant(other)
                if isinstance(other, Constant)
                else NotImplemented)

    __repr__ = generate_repr(__init__)

    @overload
    def __rmul__(self, other: FiniteNonZero) -> Term:
        ...

    @overload
    def __rmul__(self, other: RawFinite) -> Union[Term, Zero]:
        ...

    @overload
    def __rmul__(self, other: RawUnbound) -> Union[Infinite, Term, Zero]:
        ...

    @overload
    def __rmul__(self, other: Zero) -> Zero:
        ...

    @overload
    def __rmul__(self, other: Any) -> Any:
        ...

    def __rmul__(self, other: Any) -> Any:
        other = try_to_constant(other)
        return (self._multiply_by_constant(other)
                if isinstance(other, Constant)
                else NotImplemented)

    def __str__(self) -> str:
        return ((''
                 if self.scale == ONE
                 else ('-'
                       if self.scale == -ONE
                       else '{} * '.format(self.scale)))
                + 'sqrt({})'.format(self.argument))

    def _add_constant(self, other: Constant) -> Expression:
        from .form import Form
        return (Form([self], other)
                if isinstance(other, FiniteNonZero)
                else (other
                      if isinstance(other, Infinite)
                      else self))

    def _multiply_by_constant(self, other: Constant) -> Expression:
        return (Term(self.scale * other, self.argument)
                if isinstance(other, FiniteNonZero)
                else ((other if self.is_positive() else -other)
                      if isinstance(other, Infinite)
                      else other))

    def _multiply_by_term(self, other: Term) -> Expression:
        scale = self.scale * other.scale
        if self.argument == other.argument:
            return scale * self.argument
        argument, other_argument = ((self.argument, other.argument)
                                    if self.argument < other.argument
                                    else (other.argument, self.argument))
        if not other_argument % argument:
            return argument * Term.from_components(scale,
                                                   other_argument / argument)
        elif (isinstance(argument, FiniteNonZero)
              and isinstance(other_argument, FiniteNonZero)):
            arguments_gcd = math.gcd(argument.raw.numerator,
                                     other_argument.raw.numerator)
            argument /= arguments_gcd
            other_argument /= arguments_gcd
            arguments_gcd_expression = to_constant(arguments_gcd)
            assert isinstance(arguments_gcd_expression, FiniteNonZero), (
                arguments_gcd_expression
            )
            scale *= arguments_gcd_expression
        return Term.from_components(scale, argument * other_argument)
