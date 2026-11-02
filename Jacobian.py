import numpy as np
import constants

# function:
# INPUTS: theta1, theta2, theta3 (in degrees)
# OUTPUT: 3 * 3 numpy array (matrix)
def jacobian(theta1, theta2, theta3):
    t1 = np.radians(theta1)
    t2 = np.radians(theta2)
    t3 = np.radians(theta3)
    r = constants.L1 + constants.L2 * np.cos(t2) + constants.L3 * np.cos(t2 - t3)
    dr_dtheta2 = -constants.L2 * np.sin(t2) - constants.L3 * np.sin(t2 - t3)
    dr_dtheta3 = constants.L3 * np.sin(t2 - t3)
    dz_dtheta2 = constants.L2 * np.cos(t2) + constants.L3 * np.cos(t2 - t3)
    dz_dtheta3 = -constants.L3 * np.cos(t2 - t3)

    j = np.array([
        [-r * np.sin(t1), dr_dtheta2 * np.cos(t1), dr_dtheta3 * np.cos(t1)],
        [r * np.cos(t1), dr_dtheta2 * np.sin(t1), dr_dtheta3 * np.sin(t1)],
        [0, dz_dtheta2, dz_dtheta3]
    ])

    return j