import math
from contextvars import ContextVar

sqrt_evaluator = ContextVar('sqrt_evaluator',
                            default=math.sqrt)
