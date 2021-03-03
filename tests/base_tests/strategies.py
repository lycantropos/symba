from hypothesis import strategies

negative_reals = strategies.floats(max_value=0,
                                   allow_nan=False,
                                   allow_infinity=False,
                                   exclude_max=True)
non_negative_reals = strategies.floats(min_value=0,
                                       allow_nan=False,
                                       allow_infinity=False)
