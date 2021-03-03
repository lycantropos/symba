from operator import (add,
                      mul,
                      truediv)

from hypothesis import strategies

from symba.base import (Expression,
                        sqrt)
from tests.hints import Strategy
from tests.strategies import non_negative_reals

square_roots = strategies.builds(sqrt, non_negative_reals)


def to_nested_expressions(strategy: Strategy[Expression]
                          ) -> Strategy[Expression]:
    return (strategy.map(sqrt)
            | strategies.builds(add, strategy, non_negative_reals)
            | strategies.builds(add, strategy, strategy)
            | strategies.builds(mul, strategy, strategy)
            | strategies.builds(truediv, strategy, strategy.filter(bool)))


expressions = strategies.recursive(square_roots, to_nested_expressions,
                                   max_leaves=10)
expressions_pairs = strategies.tuples(expressions, expressions)
expressions_triplets = strategies.tuples(expressions, expressions, expressions)
