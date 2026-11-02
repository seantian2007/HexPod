import constants
# This is the file that stores the functions to convert between input theta1, 2, 3 and servo output pulses


def angleToPulse(angle, Leg, Joint):
    zeroPulse = 1500 # default value
    if Leg == "TestLeg":
        if Joint == "coxa":
            zeroPulse = constants.Legs.TestLeg.COXA_ZERO_PULSE
            min = constants.Legs.COXA_RANGE_DEGREE[0]
            max = constants.Legs.COXA_RANGE_DEGREE[1]
            if not (angle >= min and angle <= max):
                return None
            else:
                #u = angle / (max - min) # number between -0.5 and 0.5
                pulse = zeroPulse + angle * constants.PULSE_PER_DEGREE
                return pulse
        elif Joint == "femur":
            zeroPulse = constants.Legs.TestLeg.FEMUR_ZERO_PULSE
            min = constants.Legs.FEMUR_RANGE_DEGREE[0]
            max = constants.Legs.FEMUR_RANGE_DEGREE[1]
            if not (angle >= min and angle <= max):
                return None
            else:
                pulse = zeroPulse + angle * constants.PULSE_PER_DEGREE
                return pulse
        elif Joint == "tibia":
            zeroPulse = constants.Legs.TestLeg.TIBIA_ZERO_PULSE
            min = constants.Legs.TIBIA_RANGE_DEGREE[0]
            max = constants.Legs.TIBIA_RANGE_DEGREE[1]
            if not (angle >= min and angle <= max):
                return None
            else:
                pulse = zeroPulse + (angle - 90) * constants.PULSE_PER_DEGREE
                return pulse

    
