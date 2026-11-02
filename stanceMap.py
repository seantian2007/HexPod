import numpy as np
import constants
import matplotlib.pyplot as plt
from IKTest import ik
from Jacobian import jacobian

# take theta1 = 0, define u, z in the plane of the leg with step size of 2mm
u = np.arange(-100, 210, 2)
z = np.arange(-200, 0, 2)

torque2_percent = np.zeros((len(z),len(u)))
k = np.zeros((len(z),len(u)))
for i in range(len(u)):
    for j in range(len(z)):
        u_i = u[i]
        z_j = z[j]
        # since theta1 = 0, u = x & y = 0
        thetas = ik(u_i + constants.L1, 0, z_j)
        if thetas == None:
            torque2_percent[j, i] = np.nan
            k[j, i] = np.nan
        else:
            torque2_percent[j, i] = abs((-u_i * constants.TOTAL_WEIGHT_NEWTON / 3) * constants.KGcm_PER_Nmm) / 25
            J = jacobian(0, thetas[1], thetas[2])
            J_p = np.array([
                [J[0,1], J[0,2]],
                [J[2,1], J[2,2]]
            ])
            s = np.linalg.svd(J_p, compute_uv=False)
            k[j, i] = s[0] / s[1]

#print(torque2_percent.shape)

# fist plot
fig, ax = plt.subplots()
im = ax.imshow(torque2_percent, cmap="inferno", interpolation="nearest", aspect="equal", origin='lower', extent=[u[0], u[-1], z[0], z[-1]])

fig.colorbar(im, ax=ax, label="Intensity Scale")
ax.set_title("Torque for femur servo Pattern Analysis", fontsize=14, pad=15)

# second plot
fig1, ax1 = plt.subplots()
im1 = ax1.imshow(k, cmap="inferno", interpolation="nearest", aspect="equal", origin='lower', extent=[u[0], u[-1], z[0], z[-1]])

fig.colorbar(im1, ax=ax1, label="Intensity Scale")
ax1.set_title("Condition Number Pattern Analysis", fontsize=14, pad=15)
plt.show()
