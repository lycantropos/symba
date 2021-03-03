from hypothesis import strategies

from tests.strategies import non_negative_reals
from tests.utils import MIN_VALUE

negative_reals = strategies.floats(MIN_VALUE, 0,
                                   allow_nan=False,
                                   allow_infinity=False,
                                   exclude_max=True)
non_negative_reals = non_negative_reals
