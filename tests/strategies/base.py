from fractions import Fraction

from hypothesis import strategies

from tests.utils import (MAX_VALUE,
                         MIN_VALUE)

non_negative_reals = (strategies.integers(0, MAX_VALUE)
                      | strategies.fractions(0, MAX_VALUE,
                                             max_denominator=MAX_VALUE))
non_positive_reals = (strategies.integers(MIN_VALUE, 0)
                      | strategies.fractions(MIN_VALUE, 0,
                                             max_denominator=MAX_VALUE))
reals = (strategies.integers(MIN_VALUE, MAX_VALUE)
         | strategies.fractions(MIN_VALUE, MAX_VALUE,
                                max_denominator=MAX_VALUE))
unary_reals = strategies.just(1) | strategies.just(Fraction(1))
zero_reals = strategies.builds(int) | strategies.builds(Fraction)
negative_reals = non_positive_reals.filter(bool)
non_zero_reals = reals.filter(bool)