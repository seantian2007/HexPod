import numpy as np
from utils.Rotation import rot, Rz
from utils.fk import fk
from utils.ik import ik
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

print(f_default)

incre = 0.5 # mm
# rotate for every leg
for i in range(len(f_default[:, 0])):
    default_pos_W = f_default[i, :]
    # increment in +x
    reachlim_Pos = False
    pos_hist_L = [0, 30, 105]
    while reachlim_Pos == False:
        default_pos_W[0] += incre
        m_i_3d = np.array([m[i][0], m[i][1], 0])
        pose_L = Rz(-a[i]) @ (default_pos_W - m_i_3d)
        if ik(pose_L[0], pose_L[1], pose_L[2]) in [0, 1, 2, 3]:
            reachlim_Pos = True
            print(f"+x direction limit for Leg {i} is at {pos_hist_L}.")
        else:
            thetas = ik(pose_L[0], pose_L[1], pose_L[2])
            pos_hist_L = [thetas[0], thetas[1], thetas[2]]
