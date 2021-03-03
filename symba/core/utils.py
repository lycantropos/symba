import math
from typing import Any


def square(value: Any) -> Any:
    return value * value


def sqrt_ceil(value: int) -> int:
    value_sqrt_floor = sqrt_floor(value)
    result = value_sqrt_floor + (value > square(value_sqrt_floor))
    assert not square(result) < value
    return result


try:
    sqrt_floor = math.isqrt
except AttributeError:
    def sqrt_floor(value: int) -> int:
        if value > 0:
            candidate = 1 << (value.bit_length() + 1 >> 1)
            while True:
                next_candidate = (candidate + value // candidate) >> 1
                if next_candidate >= candidate:
                    return candidate
                candidate = next_candidate
        elif value:
            raise ValueError('Argument must be non-negative.')
        else:
            return 0
