import math
from fractions import Fraction
from numbers import Rational
from typing import (Any,
                    Sequence,
                    Tuple,
                    TypeVar)

_T1 = TypeVar('_T1')
_T2 = TypeVar('_T2')

BASE = Fraction(10)


def ceil_half(value: int) -> int:
    return -(-value // 2)


def digits_count(value: int) -> int:
    return len('%i' % abs(value))


def identity(value: _T1) -> _T1:
    return value


try:
    lcm = math.lcm
except AttributeError:
    def lcm(left: int, right: int) -> int:
        left, right = abs(left), abs(right)
        return min(left, right) * (max(left, right) // math.gcd(left, right))


def positiveness_to_sign(flag: bool) -> int:
    return 2 * flag - 1


def rational_sqrt_lower_bound(value: Rational) -> Rational:
    return Fraction(sqrt_floor(value.numerator * value.denominator),
                    value.denominator)


def rational_sqrt_upper_bound(value: Rational) -> Rational:
    return Fraction(sqrt_ceil(value.numerator * value.denominator),
                    value.denominator)


def sqrt_ceil(value: int) -> int:
    value_sqrt_floor = sqrt_floor(value)
    return value_sqrt_floor + (value != square(value_sqrt_floor))


try:
    sqrt_floor = math.isqrt
except AttributeError:
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


def perfect_sqrt(value: int, alternative: int = 1) -> int:
    candidate = sqrt_floor(value)
    return candidate if square(candidate) == value else alternative


def square(value: Any) -> Any:
    return value * value


try:
    import _symba
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
            if not remainder:
                return to_square_free(quotient)
        return value
else:
    to_square_free = _symba.to_square_free


def transpose(pairs_sequence: Sequence[Tuple[_T1, _T2]]
              ) -> Tuple[Sequence[_T1], Sequence[_T2]]:
    return tuple(zip(*pairs_sequence))
