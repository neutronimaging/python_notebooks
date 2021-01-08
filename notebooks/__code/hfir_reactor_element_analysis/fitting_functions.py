import numpy as np


def sin_fit(angle, a, m, p, b):
    """
    :parameter
    ==========
    angle: angle (in degrees)
    a: para to fit
    m: para to fit
    p: para to fit
    b: para to fit
    """
    exp_expression = a * np.sin(m * angle + p) + b
    return exp_expression
