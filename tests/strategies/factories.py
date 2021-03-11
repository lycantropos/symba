from operator import (add,
                      mul,
                      truediv)

from hypothesis import strategies

from symba.base import Expression
from tests.hints import Strategy
from .base import (non_zero_reals,
                   reals)


def to_nested_expressions(strategy: Strategy[Expression]
                          ) -> Strategy[Expression]:
    return (strategies.builds(add, strategy, reals)
            | strategies.builds(add, strategy, strategy)
            | strategies.builds(mul, strategy, reals)
            | strategies.builds(mul, strategy, strategy)
            | strategies.builds(truediv, strategy, non_zero_reals)
            | strategies.builds(truediv, reals, strategy.filter(bool))
            | strategies.builds(truediv, strategy, strategy.filter(bool)))
