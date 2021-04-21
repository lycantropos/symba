from operator import neg

from hypothesis import strategies

from symba.base import sqrt
from symba.core.constant import (One,
                                 Zero)
from tests.strategies.base import (definite_non_zero_reals,
                                   definite_reals,
                                   finite_non_negative_reals,
                                   finite_non_zero_reals,
                                   finite_reals,
                                   indefinite_reals,
                                   infinite_reals,
                                   negative_infinite_reals,
                                   positive_infinite_reals,
                                   reals,
                                   unary_reals,
                                   zero_reals)
from tests.strategies.factories import to_nested_expressions

MAX_EXPONENT = 10
MIN_EXPONENT = -MAX_EXPONENT
exponents = strategies.integers(MIN_EXPONENT, MAX_EXPONENT)
negative_exponents = strategies.integers(MIN_EXPONENT, -1)
non_negative_exponents = strategies.integers(0, MAX_EXPONENT)
positive_exponents = strategies.integers(1, MAX_EXPONENT)
digits_counts = strategies.none() | strategies.integers(-100, 100)
zero_expressions = strategies.just(Zero)
unary_expressions = strategies.just(One)
unary_reals_or_expressions = unary_reals | unary_expressions
zero_reals_or_expressions = zero_reals | zero_expressions
finite_square_roots = strategies.builds(sqrt, finite_non_negative_reals)
finite_expressions = strategies.recursive(finite_square_roots,
                                          to_nested_expressions,
                                          max_leaves=5)
finite_reals_or_expressions = finite_reals | finite_expressions
finite_non_zero_expressions = finite_expressions.filter(bool)
finite_non_zero_reals_or_expressions = (finite_non_zero_reals
                                        | finite_non_zero_expressions)
positive_infinite_expressions = strategies.builds(sqrt,
                                                  positive_infinite_reals)
negative_infinite_expressions = positive_infinite_expressions.map(neg)
infinite_expressions = (negative_infinite_expressions
                        | positive_infinite_expressions)
definite_expressions = finite_expressions | infinite_expressions
definite_reals_or_expressions = definite_reals | definite_expressions
definite_non_zero_expressions = definite_expressions.filter(bool)
definite_non_zero_reals_or_expressions = (definite_non_zero_reals
                                          | definite_non_zero_expressions)
positive_infinite_reals_or_expressions = (positive_infinite_reals
                                          | positive_infinite_expressions)
negative_infinite_reals_or_expressions = (negative_infinite_reals
                                          | negative_infinite_expressions)
infinite_reals_or_expressions = infinite_reals | infinite_expressions
indefinite_expressions = strategies.builds(sqrt, indefinite_reals)
expressions = definite_expressions | indefinite_expressions
non_zero_expressions = expressions.filter(bool)
reals_or_expressions = reals | expressions
non_zero_reals_or_expressions = (definite_non_zero_reals_or_expressions
                                 .filter(bool))
expressions_with_exponents = (
        strategies.tuples(non_zero_expressions, exponents)
        | strategies.tuples(expressions, non_negative_exponents))
definitely_dividable_expressions_with_reals_or_expressions = (
        strategies.tuples(definite_expressions,
                          finite_non_zero_reals_or_expressions)
        | strategies.tuples(finite_expressions,
                            definite_non_zero_reals_or_expressions))
definitely_dividable_reals_or_expressions_with_expressions = (
        strategies.tuples(definite_reals_or_expressions,
                          finite_non_zero_expressions)
        | strategies.tuples(finite_reals_or_expressions,
                            definite_non_zero_expressions))
definitely_multipliable_expressions_pairs = (
        strategies.tuples(finite_expressions, finite_expressions)
        | strategies.tuples(definite_non_zero_expressions,
                            definite_non_zero_expressions))
definitely_multipliable_expressions_with_reals_or_expressions = (
        strategies.tuples(finite_expressions, finite_reals_or_expressions)
        | strategies.tuples(definite_non_zero_expressions,
                            definite_non_zero_reals_or_expressions))
definitely_multipliable_expressions_triplets = (
        strategies.tuples(finite_expressions, finite_expressions,
                          finite_expressions)
        | strategies.tuples(definite_non_zero_expressions,
                            definite_non_zero_expressions,
                            definite_non_zero_expressions))
definitely_subtractable_expressions_pairs = (
        strategies.tuples(finite_expressions | positive_infinite_expressions,
                          finite_expressions | negative_infinite_expressions)
        | strategies.tuples(finite_expressions | negative_infinite_expressions,
                            finite_expressions
                            | positive_infinite_expressions))
definitely_subtractable_expressions_with_reals_or_expressions = (
        strategies.tuples(finite_expressions | positive_infinite_expressions,
                          finite_reals_or_expressions
                          | negative_infinite_reals_or_expressions)
        | strategies.tuples(finite_expressions | negative_infinite_expressions,
                            finite_reals_or_expressions
                            | positive_infinite_reals_or_expressions))
definitely_summable_expressions_with_reals_or_expressions = (
        strategies.tuples(finite_expressions | positive_infinite_expressions,
                          finite_reals_or_expressions
                          | positive_infinite_reals_or_expressions)
        | strategies.tuples(finite_expressions | negative_infinite_expressions,
                            finite_reals_or_expressions
                            | negative_infinite_reals_or_expressions))
definitely_summable_expressions_pairs = (
        strategies.tuples(finite_expressions | positive_infinite_expressions,
                          finite_expressions | positive_infinite_expressions)
        | strategies.tuples(finite_expressions | negative_infinite_expressions,
                            finite_expressions
                            | negative_infinite_expressions))
definitely_summable_expressions_triplets = (
        strategies.tuples(finite_expressions | positive_infinite_expressions,
                          finite_expressions | positive_infinite_expressions,
                          finite_expressions | positive_infinite_expressions)
        | strategies.tuples(finite_expressions | negative_infinite_expressions,
                            finite_expressions | negative_infinite_expressions,
                            finite_expressions
                            | negative_infinite_expressions))
