import pickle
from typing import TypeVar

Value = TypeVar('Value')

MAX_VALUE = 10 ** 15
MIN_VALUE = -MAX_VALUE
SQRT_MAX_VALUE = 10 ** 2
SQRT_MIN_VALUE = -MAX_VALUE


def equivalence(left_statement: bool, right_statement: bool) -> bool:
    return left_statement is right_statement


def implication(antecedent: bool, consequent: bool) -> bool:
    return not antecedent or consequent


def pickle_round_trip(value: Value) -> Value:
    return pickle.loads(pickle.dumps(value))
