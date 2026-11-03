import numpy as np

# INPUT: t - time, A - amplitude, lamda - wavelength, f - frequency
# OUTPUT: pose - (x, y, z, roll, pitch, yaw)
def wave_dance(t, A=15, lam=600, f=0.5):
    k = 2 * np.pi / lam
    omega = 2 * np.pi * f
    z = A * np.sin(omega * t)
    pitch = -np.degrees(np.atan(A * k * np.cos(omega * t)))
    return np.array([0, 0, z, 0, pitch, 0])