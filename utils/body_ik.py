import numpy as np
from .Rotation import rot, Rz
from .fk import fk
from .ik import ik
import constants

# rearrange constants in a better formuat
a = np.array([
    constants.Legs.R1Leg.alpha_R1,
    constants.Legs.R2Leg.alpha_R2,
    constants.Legs.R3Leg.alpha_R3,
    constants.Legs.L1Leg.alpha_L1,
    constants.Legs.L2Leg.alpha_L2,
    constants.Legs.L3Leg.alpha_L3
])
m = np.array([
    constants.Legs.R1Leg.m_R1,
    constants.Legs.R2Leg.m_R2,
    constants.Legs.R3Leg.m_R3,
    constants.Legs.L1Leg.m_L1,
    constants.Legs.L2Leg.m_L2,
    constants.Legs.L3Leg.m_L3
])
# calculate default feet pose (standing)

# get the pose of toe in W from pose in L
# a_i in degrees, m_i in mm (tuple form)
def get_fi(a_i, m_i):
    m_i_3d = np.array([m_i[0], m_i[1], 0])
    x, y, z = fk(0, constants.Legs.STAND_FEMUR, constants.Legs.STAND_TIBIA)
    return Rz(a_i) @ np.array([x, y, z]) + m_i_3d

f_default = np.zeros((6,3))
for i in range(6):
    f_default[i, :] = get_fi(a[i], m[i])

# INPUT: pose = [x, y, z, roll, pitch, yaw], feetPose = 6*3 matrix specifying the Pose of six toes in W
# OUTPUT: thetas (6,3), status (6,2); rows are Legs
def body_ik(pose, feetPose=f_default):
    R = rot(pose[3], pose[4], pose[5])
    t = np.array([pose[0], pose[1], pose[2]])
    p_L = np.zeros((6,3))
    thetas = np.zeros((6,3))
    status = np.zeros((6,2))

    for i in range(6):
        p = Rz(-a[i]) @ (np.transpose(R) @ (feetPose[i, :] - t) - np.array([m[i][0], m[i][1], 0]))
        p_L[i, :] = p
        theta = ik(p[0], p[1], p[2])

        if theta not in [0, 1, 2, 3]:
            thetas[i, :] = np.array([theta[0], theta[1], theta[2]])
            status[i, 0] = True
            status[i, 1] = np.nan
        else:
            thetas[i, :] = np.array([np.nan, np.nan, np.nan])
            status[i, 0] = False
            status[i, 1] = theta

    return thetas, status