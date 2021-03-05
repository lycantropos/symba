from hypothesis import strategies

from tests.utils import (MAX_VALUE,
                         MIN_VALUE)

non_negative_reals = strategies.floats(0, MAX_VALUE,
                                       allow_nan=False,
                                       allow_infinity=False)
reals = strategies.floats(MIN_VALUE, MAX_VALUE,
                          allow_nan=False,
                          allow_infinity=False)
zero_reals = strategies.just(0)
