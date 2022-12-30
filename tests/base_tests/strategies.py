from operator import neg

from hypothesis import strategies

from symba.base import sqrt
from tests.strategies.base import (finite_non_negative_reals,
                                   negative_reals,
                                   non_negative_reals,
                                   positive_infinite_reals)
from tests.strategies.factories import to_nested_expressions

finite_square_roots = strategies.builds(sqrt, finite_non_negative_reals)
square_roots = strategies.builds(sqrt, non_negative_reals)
positive_infinite_expressions = strategies.builds(sqrt,
                                                  positive_infinite_reals)
negative_infinite_expressions = positive_infinite_expressions.map(neg)
infinite_expressions = (negative_infinite_expressions
                        | positive_infinite_expressions)
finite_expressions = strategies.recursive(finite_square_roots,
                                          to_nested_expressions,
                                          max_leaves=3)
expressions = finite_expressions | infinite_expressions
non_negative_reals_or_expressions = (non_negative_reals
                                     | expressions.map(abs))
negative_reals_or_expressions = (negative_reals
                                 | (expressions.filter(bool)
                                    .map(abs).map(neg)))
reals_or_expressions = (negative_reals_or_expressions
                        | non_negative_reals_or_expressions)
