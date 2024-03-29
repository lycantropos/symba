import math
import sys
from numbers import Rational
from typing import (Callable,
                    Sequence,
                    Tuple,
                    TypeVar)

from cfractions import Fraction

from .hints import RawConstant

_T1 = TypeVar('_T1')
_T2 = TypeVar('_T2')

BASE = Fraction(10)


def ceil_half(value: int) -> int:
    return -(-value // 2)


def digits_count(value: int) -> int:
    return len('%i' % abs(value))


def identity(value: _T1) -> _T1:
    return value


if sys.version_info < (3, 9):
    def lcm(left: int, right: int) -> int:
        left, right = abs(left), abs(right)
        return min(left, right) * (max(left, right) // math.gcd(left, right))
else:
    lcm = math.lcm


def positiveness_to_sign(flag: bool) -> int:
    return 2 * flag - 1


def rational_sqrt_lower_bound(value: RawConstant) -> Fraction:
    assert isinstance(value, Rational), value
    return Fraction(sqrt_floor(value.numerator * value.denominator),
                    value.denominator)


def rational_sqrt_upper_bound(value: RawConstant) -> Fraction:
    assert isinstance(value, Rational), value
    return Fraction(sqrt_ceil(value.numerator * value.denominator),
                    value.denominator)


def sqrt_ceil(value: int) -> int:
    value_sqrt_floor = sqrt_floor(value)
    return value_sqrt_floor + (value != value_sqrt_floor * value_sqrt_floor)


if sys.version_info < (3, 8):
    def sqrt_floor(value: int) -> int:
        if value > 0:
            candidate = 1 << ((value.bit_length() + 1) >> 1)
            while True:
                next_candidate = (candidate + value // candidate) >> 1
                if next_candidate >= candidate:
                    return candidate
                candidate = next_candidate
        else:
            assert not value, 'Argument should be non-negative.'
            return 0
else:
    sqrt_floor = math.isqrt


def perfect_sqrt(value: int, alternative: int = 1) -> int:
    candidate = sqrt_floor(value)
    return candidate if candidate * candidate == value else alternative


to_square_free: Callable[[int], int]

try:
    from symba._symba import to_square_free
except ImportError:
    def to_square_free(value: int) -> int:
        while value % 4 == 0:
            value //= 4
        factor_candidate_squared = 1
        for factor_candidate_base in range(1, value, 2):
            factor_candidate_squared += 4 * factor_candidate_base + 4
            if factor_candidate_squared > value:
                break
            quotient, remainder = divmod(value, factor_candidate_squared)
            while not remainder:
                value = quotient
                quotient, remainder = divmod(value, factor_candidate_squared)
        return value


def transpose(
        pairs_sequence: Sequence[Tuple[_T1, _T2]]
) -> Tuple[Sequence[_T1], Sequence[_T2]]:
    first_coordinates, second_coordinates = zip(*pairs_sequence)
    return first_coordinates, second_coordinates
