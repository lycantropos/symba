from operator import (add,
                      mul,
                      truediv)

from hypothesis import strategies

from symba.base import (Expression,
                        sqrt)
from symba.core.constant import (One,
                                 Zero)
from tests.hints import Strategy
from tests.strategies import (non_negative_reals,
                              reals,
                              unary_reals,
                              zero_reals)

digits_counts = strategies.none() | strategies.integers(-100, 100)
zero_expressions = strategies.just(Zero)
unary_expressions = strategies.just(One)
unary_reals_or_expressions = unary_reals | unary_expressions
zero_reals_or_expressions = zero_reals | zero_expressions
non_zero_reals = reals.filter(bool)


def to_nested_expressions(strategy: Strategy[Expression]
                          ) -> Strategy[Expression]:
    return (strategies.builds(add, strategy, reals)
            | strategies.builds(add, strategy, strategy)
            | strategies.builds(mul, strategy, reals)
            | strategies.builds(mul, strategy, strategy)
            | strategies.builds(truediv, strategy, non_zero_reals)
            | strategies.builds(truediv, reals, strategy.filter(bool))
            | strategies.builds(truediv, strategy, strategy.filter(bool)))


sqrt_arguments = strategies.recursive(strategies.builds(sqrt,
                                                        non_negative_reals),
                                      to_nested_expressions,
                                      max_leaves=5)


def safe_sqrt(expression: Expression) -> Expression:
    try:
        return sqrt(expression)
    except ValueError:
        return expression


expressions = sqrt_arguments.map(safe_sqrt)
reals_or_expressions = reals | expressions
non_zero_expressions = expressions.filter(bool)
non_zero_reals_or_expressions = non_zero_reals | non_zero_expressions
