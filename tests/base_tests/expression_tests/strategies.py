from operator import (add,
                      mul,
                      truediv)

from hypothesis import strategies

from symba.base import (Expression,
                        sqrt)
from symba.core.constant import Zero
from tests.hints import Strategy
from tests.strategies import (non_negative_reals,
                              reals,
                              zero_reals)

digits_counts = strategies.none() | strategies.integers(-100, 100)
zero_reals_or_expressions = zero_reals | strategies.just(Zero)
non_zero_reals = reals.filter(bool)


def to_nested_expressions(strategy: Strategy[Expression]
                          ) -> Strategy[Expression]:
    return (strategy.filter(lambda value: value >= 0).map(sqrt)
            | strategies.builds(add, strategy, reals)
            | (strategies.lists(strategy,
                                min_size=2,
                                max_size=10)
               .map(sum))
            | strategies.builds(mul, strategy, reals)
            | strategies.builds(mul, strategy, strategy)
            | strategies.builds(truediv, strategy, non_zero_reals)
            | strategies.builds(truediv, reals, strategy.filter(bool))
            | strategies.builds(truediv, strategy, strategy.filter(bool)))


expressions = strategies.recursive(strategies.builds(sqrt, non_negative_reals),
                                   to_nested_expressions,
                                   max_leaves=10)
reals_or_expressions = reals | expressions
non_zero_expressions = expressions.filter(bool)
non_zero_reals_or_expressions = non_zero_reals | non_zero_expressions
