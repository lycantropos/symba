import math
from fractions import Fraction
from numbers import Rational
from typing import Any


def ceil_half(value: int) -> int:
    return -(-value // 2)


def integer_digits_count(value: int) -> int:
    return len('%i' % abs(value))


try:
    lcm = math.lcm
except AttributeError:
    def lcm(left: int, right: int) -> int:
        left, right = abs(left), abs(right)
        return min(left, right) * (max(left, right) // math.gcd(left, right))


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
