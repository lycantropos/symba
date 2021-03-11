import math
from numbers import (Rational,
                     Real)
from typing import (TYPE_CHECKING,
                    Any,
                    Optional,
                    Tuple,
                    Union)

from reprit.base import generate_repr

from symba.core.utils import (ceil_half,
                              rational_sqrt_lower_bound,
                              rational_sqrt_upper_bound,
                              square)
from . import context
from .abcs import Expression
from .constant import (Constant,
                       One,
                       Zero)
from .hints import SqrtEvaluator

if TYPE_CHECKING:
    from .form import Form


class Term(Expression):
    @classmethod
    def from_components(cls,
                        scale: Constant,
                        argument: Expression) -> Expression:
        if not (scale and argument):
            return Zero
        denominator, argument = argument.extract_common_denominator()
        scale /= denominator
        argument *= denominator
        argument_perfect_sqrt = argument.perfect_sqrt()
        argument_perfect_part = argument_perfect_sqrt.square()
        return (argument_perfect_sqrt * scale
                if argument == argument_perfect_part
                else (argument_perfect_sqrt
                      * cls(scale, argument / argument_perfect_part)))

    __slots__ = 'argument', 'scale'

    def __init__(self, scale: Constant, argument: Expression) -> None:
        self.scale, self.argument = scale, argument

    def evaluate(self, sqrt_evaluator: Optional[SqrtEvaluator] = None) -> Real:
        return (self.scale.evaluate(sqrt_evaluator)
                * ((context.sqrt_evaluator.get()
                    if sqrt_evaluator is None
                    else sqrt_evaluator)
                   (self.argument.evaluate(sqrt_evaluator))))

    def extract_common_denominator(self) -> Tuple[int, 'Term']:
        common_denominator, scale = self.scale.extract_common_denominator()
        return common_denominator, Term(scale, self.argument)

    def extract_common_numerator(self) -> Tuple[int, 'Term']:
        common_numerator, scale = self.scale.extract_common_numerator()
        return common_numerator, Term(scale, self.argument)

    def inverse(self) -> 'Term':
        return Term.from_components(self.scale.inverse(),
                                    self.argument.inverse())

    def is_positive(self) -> bool:
        return self.scale > 0

    def lower_bound(self) -> Rational:
        return (rational_sqrt_lower_bound(self.square().lower_bound())
                if self.is_positive()
                else -(-self).upper_bound())

    def perfect_sqrt(self) -> Expression:
        return self.scale.perfect_sqrt()

    def significant_digits_count(self) -> int:
        return ceil_half(self.square().significant_digits_count())

    def square(self) -> Expression:
        return self.scale.square() * self.argument

    def upper_bound(self) -> Rational:
        return (rational_sqrt_upper_bound(self.square().upper_bound())
                if self.is_positive()
                else -(-self).lower_bound())

    def __abs__(self) -> 'Term':
        return Term(abs(self.scale), self.argument)

    def __add__(self, other: Union[Real, Expression]) -> Expression:
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

    def __eq__(self, other: Any) -> Any:
        return (self.is_positive() is other.is_positive()
                and self.square() == other.square()
                if isinstance(other, Expression)
                else NotImplemented)

    def __ge__(self, other: Union[Real, Expression]) -> bool:
        return ((other <= 0 or square(other) <= self.square()
                 if self.is_positive()
                 else other <= 0 and square(other) >= self.square())
                if isinstance(other, Real)
                else ((not other.is_positive()
                       or other.square() <= self.square()
                       if self.is_positive()
                       else (not other.is_positive()
                             and other.square() >= self.square()))
                      if isinstance(other, Expression)
                      else NotImplemented))

    def __gt__(self, other: Union[Real, Expression]) -> bool:
        return ((other <= 0 or square(other) < self.square()
                 if self.is_positive()
                 else other <= 0 and square(other) > self.square())
                if isinstance(other, Real)
                else ((not other.is_positive()
                       or other.square() < self.square()
                       if self.is_positive()
                       else (not other.is_positive()
                             and other.square() > self.square()))
                      if isinstance(other, Expression)
                      else NotImplemented))

    def __hash__(self) -> int:
        return hash((self.is_positive(), self.square()))

    def __le__(self, other: Union[Real, Expression]) -> bool:
        return ((other > 0 and square(other) >= self.square()
                 if self.is_positive()
                 else other > 0 or square(other) <= self.square())
                if isinstance(other, (Real, Constant, Term))
                else ((other.is_positive()
                       and other.square() >= self.square()
                       if self.is_positive()
                       else (other.is_positive()
                             or other.square() <= self.square()))
                      if isinstance(other, Expression)
                      else NotImplemented))

    def __lt__(self, other: Union[Real, Expression]) -> bool:
        return ((other > 0 and square(other) > self.square()
                 if self.is_positive()
                 else other > 0 or square(other) < self.square())
                if isinstance(other, (Real, Constant, Term))
                else ((other.is_positive()
                       and other.square() > self.square()
                       if self.is_positive()
                       else (other.is_positive()
                             or other.square() < self.square()))
                      if isinstance(other, Expression)
                      else NotImplemented))

    def __mul__(self, other: Union[Real, Expression]) -> Expression:
        return ((Term(self.scale * other, self.argument)
                 if other
                 else Zero)
                if isinstance(other, (Real, Constant))
                else (self._multiply_with_term(other)
                      if isinstance(other, Term)
                      else NotImplemented))

    def __neg__(self) -> 'Term':
        return Term(-self.scale, self.argument)

    def __radd__(self, other: Union[Real, Expression]) -> Expression:
        from .form import Form
        return (Form.from_components(self,
                                     tail=Constant(other))
                if isinstance(other, Real)
                else (Form.from_components(self,
                                           tail=other)
                      if isinstance(other, Constant)
                      else NotImplemented))

    __repr__ = generate_repr(__init__)

    def __rmul__(self, other: Union[Real, Expression]) -> Expression:
        return ((Term(self.scale * other, self.argument)
                 if other
                 else Zero)
                if isinstance(other, (Real, Constant))
                else NotImplemented)

    def __str__(self) -> str:
        return ((''
                 if self.scale == One
                 else ('-'
                       if self.scale == -One
                       else '{} * '.format(self.scale)))
                + 'sqrt({})'.format(self.argument))

    def _multiply_with_term(self, other: 'Term') -> Expression:
        scale = self.scale * other.scale
        if self.argument == other.argument:
            return scale * self.argument
        argument, other_argument = ((self.argument, other.argument)
                                    if self.argument < other.argument
                                    else (other.argument, self.argument))
        if not other_argument % argument:
            return argument * Term.from_components(scale,
                                                   other_argument / argument)
        elif (isinstance(argument, Constant)
              and isinstance(other_argument, Constant)):
            arguments_gcd = math.gcd(argument.value.numerator,
                                     other_argument.value.numerator)
            argument /= arguments_gcd
            other_argument /= arguments_gcd
            scale *= arguments_gcd
        return Term.from_components(scale, argument * other_argument)
