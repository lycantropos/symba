import math
from operator import neg

from hypothesis import strategies

from symba.base import sqrt
from tests.strategies.factories import to_nested_expressions
from tests.strategies.sqrt_base import (definite_negative_reals,
                                        definite_non_negative_reals,
                                        finite_non_negative_reals,
                                        positive_infinite_reals)

finite_square_roots = strategies.builds(sqrt, finite_non_negative_reals)
definite_square_roots = strategies.builds(sqrt, definite_non_negative_reals)
positive_infinite_expressions = strategies.builds(sqrt,
                                                  positive_infinite_reals)
negative_infinite_expressions = positive_infinite_expressions.map(neg)
infinite_expressions = (negative_infinite_expressions
                        | positive_infinite_expressions)
finite_expressions = strategies.recursive(finite_square_roots,
                                          to_nested_expressions,
                                          max_leaves=5)
definite_expressions = finite_expressions | infinite_expressions
definite_non_negative_reals_or_expressions = (definite_non_negative_reals
                                              | definite_expressions.map(abs))
definite_negative_reals_or_expressions = (definite_negative_reals
                                          | (definite_expressions.filter(bool)
                                             .map(abs).map(neg)))
definite_reals_or_expressions = (definite_negative_reals_or_expressions
                                 | definite_non_negative_reals_or_expressions)
sqrt_evaluators = strategies.just(math.sqrt)
