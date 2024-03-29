import math
from fractions import Fraction

from hypothesis import strategies

from tests.utils import (MAX_VALUE,
                         MIN_VALUE)

finite_non_negative_reals = (strategies.integers(0, MAX_VALUE)
                             | strategies.fractions(0, MAX_VALUE,
                                                    max_denominator=MAX_VALUE))
finite_non_positive_reals = (strategies.integers(MIN_VALUE, 0)
                             | strategies.fractions(MIN_VALUE, 0,
                                                    max_denominator=MAX_VALUE))
finite_negative_reals = finite_non_positive_reals.filter(bool)
finite_reals = (strategies.integers(MIN_VALUE, MAX_VALUE)
                | strategies.fractions(MIN_VALUE, MAX_VALUE,
                                       max_denominator=MAX_VALUE))
unary_reals = strategies.just(1) | strategies.just(Fraction(1))
zero_reals = strategies.builds(int) | strategies.builds(Fraction)
finite_non_zero_reals = finite_reals.filter(bool)
negative_infinite_reals = strategies.just(-math.inf)
positive_infinite_reals = strategies.just(math.inf)
negative_reals = finite_negative_reals | negative_infinite_reals
non_negative_reals = finite_non_negative_reals | positive_infinite_reals
non_positive_reals = finite_non_positive_reals | negative_infinite_reals
infinite_reals = negative_infinite_reals | positive_infinite_reals
reals = finite_reals | infinite_reals
non_zero_reals = reals.filter(bool)
