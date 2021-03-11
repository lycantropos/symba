import math
from operator import neg

from hypothesis import strategies

from symba.base import sqrt
from tests.strategies import (negative_reals,
                              non_negative_reals,
                              to_nested_expressions)

square_roots = strategies.builds(sqrt, non_negative_reals)
expressions = square_roots | to_nested_expressions(square_roots)
non_negative_reals_or_expressions = (non_negative_reals
                                     | expressions.map(abs))
negative_reals_or_expressions = (negative_reals
                                 | expressions.filter(bool).map(abs).map(neg))
sqrt_evaluators = strategies.just(math.sqrt)
