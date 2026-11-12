from typing import Final
import numpy as np

# unit converstion constnat
KGcm_PER_Nmm: Final = 0.01019716 # times this constant by Nmm will get KGcm

# hardware const
## length of three parts on one leg
L1: Final = 62
L2: Final = 76
L3: Final = 132

TOTAL_WEIGHT_NEWTON: Final = 21.57 # TODO: change this

# convert util const
PULSE_PER_DEGREE: Final =  2000 / 180
DEGREE_PER_PULSE: Final = 180/ 2000

# kinetics const
MAX_LINEAR_SPEED = 40 # mm/s

# list of zero pulse in this order: R1, R2, R3, L1, L2, L3; inside each Leg: coxa, femur, tibia
#ZERO_PULSE: Final = [1480, 1540, 1550, 1520, 1490, 1520, 1410, 1470, 1530, 1450, 1580, 1510, 1490, 1470, 1470, 1540, 1480, 1500]
ZERO_PULSE: Final = [1480, 1580, 1550, 1520, 1490, 1520, 1410, 1480, 1530, 1450, 1580, 1510, 1490, 1470, 1470, 1540, 1500, 1500]

# default toe position in world coords
F_DEFAULT: Final = np.array([
    [ 2.25480566e+02, -1.30191022e+02, -8.95022091e+01],
    [ 9.91853962e-15, -2.60382045e+02, -8.95022091e+01],
    [-2.25480566e+02, -1.30191022e+02, -8.95022091e+01],
    [ 2.25480566e+02,  1.30191022e+02, -8.95022091e+01],
    [ 9.91853962e-15,  2.60382045e+02, -8.95022091e+01],
    [-2.25480566e+02,  1.30191022e+02, -8.95022091e+01],
])

# Leg-specific const
class Legs:
    # constant universal to every leg
    COXA_RANGE_DEGREE: Final = (-45, 45)
    FEMUR_RANGE_DEGREE: Final = (-75, 75)
    TIBIA_RANGE_DEGREE: Final = (15, 165)

    # special pose:
    STAND_FEMUR: Final = 30 # degrees
    STAND_TIBIA: Final = 105 # degrees

    
    class TestLeg:
        COXA_ZERO_PULSE: Final = 1570
        FEMUR_ZERO_PULSE: Final = 1460
        TIBIA_ZERO_PULSE: Final = 1530

    class R1Leg:
        m_R1: Final = (85.2, -49.2) # mm
        alpha_R1: Final = -30 # degrees

    class R2Leg:
        m_R2: Final = (0, -98.4) # mm
        alpha_R2: Final = -90 # degrees

    class R3Leg:
        m_R3: Final = (-85.2, -49.2) # mm
        alpha_R3: Final = -150 # degrees

    class L1Leg:
        m_L1: Final = (85.2, 49.2) # mm
        alpha_L1: Final = 30 # degrees

    class L2Leg:
        m_L2: Final = (0, 98.4) # mm
        alpha_L2: Final = 90 # degrees

    class L3Leg:
        m_L3: Final = (-85.2, 49.2) # mm
        alpha_L3: Final = 150 # degrees
