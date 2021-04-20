from operator import (add,
                      mul)

from hypothesis import strategies

from symba.base import Expression
from tests.hints import Strategy


def to_nested_expressions(strategy: Strategy[Expression]
                          ) -> Strategy[Expression]:
    return (strategies.builds(add, strategy, strategy)
            | strategies.builds(mul, strategy, strategy))
