from operator import (add,
                      mul,
                      truediv)

from hypothesis import strategies

from symba.base import Expression
from tests.hints import Strategy
from .base import (finite_non_zero_reals,
                   finite_reals)


def to_nested_expressions(strategy: Strategy[Expression]
                          ) -> Strategy[Expression]:
    return (strategies.builds(add, strategy, finite_reals)
            | strategies.builds(add, strategy, strategy)
            | strategies.builds(mul, strategy, finite_reals)
            | strategies.builds(mul, strategy, strategy)
            | strategies.builds(truediv, strategy, finite_non_zero_reals)
            | strategies.builds(truediv, finite_reals, strategy.filter(bool))
            | strategies.builds(truediv, strategy, strategy.filter(bool)))
