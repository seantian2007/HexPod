import constants
import numpy as np
# This is the file that stores the functions to convert between input theta1, 2, 3 and servo output pulses

# input: angle list of size 18
def angleToPulse(anglelst):
    s = 1 # default value
    outputPulse = np.zeros(len(anglelst))

    if len(anglelst) != 18:
        return None

    for i, angle in enumerate(anglelst):
        if i >= 9:
            s = -1

        if i % 3 == 0:
            zeroPulse = constants.ZERO_PULSE[i]
            min = constants.Legs.COXA_RANGE_DEGREE[0]
            max = constants.Legs.COXA_RANGE_DEGREE[1]
            if not (angle >= min and angle <= max):
                return None
            else:
                #u = angle / (max - min) # number between -0.5 and 0.5
                pulse = zeroPulse + angle * constants.PULSE_PER_DEGREE
                outputPulse[i] = pulse
        elif i % 3 == 1:
            zeroPulse = constants.ZERO_PULSE[i]
            min = constants.Legs.FEMUR_RANGE_DEGREE[0]
            max = constants.Legs.FEMUR_RANGE_DEGREE[1]
            if not (angle >= min and angle <= max):
                return None
            else:
                pulse = zeroPulse + s * angle * constants.PULSE_PER_DEGREE
                outputPulse[i] = pulse
        elif i % 3 == 2:
            zeroPulse = constants.ZERO_PULSE[i]
            min = constants.Legs.TIBIA_RANGE_DEGREE[0]
            max = constants.Legs.TIBIA_RANGE_DEGREE[1]
            if not (angle >= min and angle <= max):
                return None
            else:
                pulse = zeroPulse + s * (angle - 90) * constants.PULSE_PER_DEGREE
                outputPulse[i] = pulse

    return outputPulse

    
