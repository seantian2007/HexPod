from typing import Final

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
# Leg-specific const
class Legs:
    # constant universal to every leg
    COXA_RANGE_DEGREE: Final = (-45, 45)
    FEMUR_RANGE_DEGREE: Final = (-75, 75)
    TIBIA_RANGE_DEGREE: Final = (15, 165)
    
    class TestLeg:
        COXA_ZERO_PULSE: Final = 1570
        FEMUR_ZERO_PULSE: Final = 1460
        TIBIA_ZERO_PULSE: Final = 1530
