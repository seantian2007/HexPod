import numpy as np
import constants
from .gaits import leg_phase, GAITS

def feet_straight(t, T, S, h, gait):
    f = constants.F_DEFAULT.copy() # default value of size (6, 3)
    beta = GAITS[gait][0]
    for i in range(6):
        (in_stance, s) = leg_phase(i, t, T, gait)
        if in_stance == True:
            x = f[i, 0].copy() + S/2 - S * s
            f[i, 0] = x
        else:
            lamda = S / beta
            c = s - np.sin(2 * np.pi * s) / (2 * np.pi)
            x = f[i, 0].copy() - S / 2 + lamda * c - lamda * (1 - beta) * s
            z = f[i, 2].copy() + h * (1 - np.cos(2 * np.pi * s)) / 2
            f[i, 0] = x
            f[i, 2] = z

    return f