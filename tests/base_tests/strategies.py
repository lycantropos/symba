import math

from hypothesis import strategies

from tests.strategies import (negative_reals,
                              non_negative_reals)

negative_reals = negative_reals
non_negative_reals = non_negative_reals
sqrt_evaluators = strategies.just(math.sqrt)
