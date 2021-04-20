import math
from operator import neg

from hypothesis import strategies

from symba.base import sqrt
from tests.strategies import (definite_negative_reals,
                              definite_non_negative_reals,
                              finite_non_negative_reals,
                              to_nested_expressions)

finite_square_roots = strategies.builds(sqrt, finite_non_negative_reals)
definite_square_roots = strategies.builds(sqrt, definite_non_negative_reals)
definite_expressions = strategies.recursive(definite_square_roots,
                                            to_nested_expressions,
                                            max_leaves=10)
definite_non_negative_reals_or_expressions = (definite_non_negative_reals
                                              | definite_expressions.map(abs))
definite_negative_reals_or_expressions = (definite_negative_reals
                                          | (definite_expressions.filter(bool)
                                             .map(abs).map(neg)))
sqrt_evaluators = strategies.just(math.sqrt)
