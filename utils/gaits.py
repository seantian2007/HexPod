
GAITS = {
    "tripod": (0.5, (0, 0.5, 0, 0.5, 0, 0.5)),
    "ripple": (2/3, (1/6, 5/6, 1/2, 2/3, 1/3, 0)),
    "wave": (5/6, (1/3, 1/6, 0, 5/6, 2/3, 1/2))
}

## INPUTS:
# leg: 0-5 (R1, R2, R3, L1, L2, L3)
# t: current time
# T: period
# gait: gait patterns (keys in GAITS)
## OUTPUTS: (in_stance, s)
# in_stance: True = standing, False = not standing
# s = progress of the leg from 0 t0 1
def leg_phase(leg, t, T, gait):
    beta = GAITS[gait][0]
    delta = GAITS[gait][1][leg]

    phi = (t/T - delta) % 1
    in_stance = False # default value
    if phi < beta:
        in_stance = True

    s = 0
    if in_stance == True:
        s = phi / beta
    else:
        s = (phi - beta) / (1 - beta)

    return (in_stance, s)
