from hypothesis import strategies

non_negative_reals = strategies.floats(min_value=0,
                                       allow_nan=False,
                                       allow_infinity=False)
