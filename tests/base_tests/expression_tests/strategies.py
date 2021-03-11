from hypothesis import strategies

from symba.base import sqrt
from symba.core.constant import (One,
                                 Zero)
from tests.strategies import (non_negative_reals,
                              non_zero_reals,
                              reals,
                              to_nested_expressions,
                              unary_reals,
                              zero_reals)

digits_counts = strategies.none() | strategies.integers(-100, 100)
zero_expressions = strategies.just(Zero)
unary_expressions = strategies.just(One)
unary_reals_or_expressions = unary_reals | unary_expressions
zero_reals_or_expressions = zero_reals | zero_expressions
square_roots = strategies.builds(sqrt, non_negative_reals)
expressions = square_roots | to_nested_expressions(square_roots)
reals_or_expressions = reals | expressions
non_zero_expressions = expressions.filter(bool)
non_zero_reals_or_expressions = non_zero_reals | non_zero_expressions
