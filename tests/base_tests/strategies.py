from hypothesis import strategies

from tests.strategies import non_negative_reals

negative_reals = strategies.floats(max_value=0,
                                   allow_nan=False,
                                   allow_infinity=False,
                                   exclude_max=True)
non_negative_reals = non_negative_reals
