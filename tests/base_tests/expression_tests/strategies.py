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

MAX_EXPONENT = 10
MIN_EXPONENT = -MAX_EXPONENT
exponents = strategies.integers(MIN_EXPONENT, MAX_EXPONENT)
negative_exponents = strategies.integers(MIN_EXPONENT, -1)
non_negative_exponents = strategies.integers(0, MAX_EXPONENT)
positive_exponents = strategies.integers(1, MAX_EXPONENT)
digits_counts = strategies.none() | strategies.integers(-100, 100)
zero_expressions = strategies.just(Zero)
unary_expressions = strategies.just(One)
unary_reals_or_expressions = unary_reals | unary_expressions
zero_reals_or_expressions = zero_reals | zero_expressions
square_roots = strategies.builds(sqrt, non_negative_reals)
expressions = strategies.recursive(square_roots,
                                   to_nested_expressions,
                                   max_leaves=5)
reals_or_expressions = reals | expressions
non_zero_expressions = expressions.filter(bool)
non_zero_reals_or_expressions = non_zero_reals | non_zero_expressions
expressions_with_exponents = (
        strategies.tuples(non_zero_expressions, exponents)
        | strategies.tuples(expressions, non_negative_exponents))
