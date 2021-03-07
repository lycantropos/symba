import math
from numbers import (Rational,
                     Real)
from typing import (TYPE_CHECKING,
                    Any,
                    Optional,
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
    __slots__ = 'argument', 'scale'

    @classmethod
    def from_components(cls,
                        scale: Constant,
                        argument: Expression) -> Expression:
        if not (scale and argument):
            return Zero
        argument_perfect_scale_sqrt = argument.perfect_sqrt()
        if argument == argument_perfect_scale_sqrt.square():
            return argument_perfect_scale_sqrt * scale
        return argument_perfect_scale_sqrt * cls(scale, argument)

    def evaluate(self, sqrt_evaluator: Optional[SqrtEvaluator] = None) -> Real:
        return (self.scale.evaluate(sqrt_evaluator)
                * ((context.sqrt_evaluator.get()
                    if sqrt_evaluator is None
                    else sqrt_evaluator)
                   (self.argument.evaluate(sqrt_evaluator))))

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

    def __init__(self, scale: Constant, argument: Expression) -> None:
        self.scale, self.argument = scale, argument

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

    def __rtruediv__(self, other: Union[Real, Expression]) -> Expression:
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

    def __truediv__(self, other: Union[Real, Expression]) -> Expression:
        return (Term(self.scale / other, self.argument)
                if isinstance(other, (Real, Constant))
                else (self._multiply_with_term(One / other)
                      if isinstance(other, Term)
                      else NotImplemented))

    def _multiply_with_term(self, other: 'Term') -> Expression:
        from .ratio import Ratio
        scale = self.scale * other.scale
        argument, other_argument = self.argument, other.argument
        arguments_ratio = other_argument / argument
        if not isinstance(arguments_ratio, Ratio):
            return argument * Term.from_components(scale, arguments_ratio)
        elif (isinstance(argument, Constant)
              and isinstance(other_argument, Constant)):
            arguments_gcd = math.gcd(argument.value.numerator,
                                     other_argument.value.numerator)
            argument /= arguments_gcd
            other_argument /= arguments_gcd
            scale *= arguments_gcd
        return Term.from_components(scale, argument * other_argument)
