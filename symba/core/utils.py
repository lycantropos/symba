import math
from fractions import Fraction
from numbers import Rational
from typing import (Any,
                    List,
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
        elif value:
            raise ValueError('Argument must be non-negative.')
        else:
            return 0


def square(value: Any) -> Any:
    return value * value


def to_binary_digits(value: int) -> List[int]:
    for _ in range(value.bit_length()):
        yield value % 2
        value >>= 1


def transpose(pairs_sequence: Sequence[Tuple[_T1, _T2]]
              ) -> Tuple[Sequence[_T1], Sequence[_T2]]:
    return tuple(zip(*pairs_sequence))
