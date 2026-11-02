import numpy as np
import math
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

# define length in mm
L1 = 62
L2 = 76
L3 = 132

# standard theta lists for checking:
theta1 = [0, 0, 30, 0, -20, 0, 45]
theta2 = [0, 0, 0, 30, 30, 45, -20]
theta3 = [0, 90, 90, 105, 105, 135, 60]

# input angles in lists
def fk(theta1, theta2, theta3):
    r = L1 + L2 * np.cos(np.deg2rad(theta2)) + L3 * np.cos(np.deg2rad(np.subtract(theta2, theta3)))
    x = r * np.cos(np.deg2rad(theta1))
    y = r * np.sin(np.deg2rad(theta1))
    z = L2 * np.sin(np.deg2rad(theta2)) + L3 * np.sin(np.deg2rad(np.subtract(theta2, theta3)))
    return x, y, z

def fk_matrix(theta1, theta2, theta3):
    toe = np.zeros((len(theta1),3))
    knee = np.zeros((len(theta1),3))
    femur = np.zeros((len(theta1),3))

    for i in range(len(theta1)):
        theta1_rad = np.deg2rad(theta1[i])
        theta2_rad = np.deg2rad(theta2[i])
        theta3_rad = np.deg2rad(theta3[i])

        Rz_theta1 = np.array([[np.cos(theta1_rad), -np.sin(theta1_rad), 0, 0], 
                    [np.sin(theta1_rad), np.cos(theta1_rad), 0, 0],
                    [0, 0, 1, 0],
                    [0, 0, 0, 1]])
        Tx_L1 = np.array([[1, 0, 0, L1],
                [0, 1, 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1]])
        Ry_theta2 = np.array([[np.cos(-theta2_rad), 0, np.sin(-theta2_rad), 0],
                    [0, 1, 0, 0],
                    [-np.sin(-theta2_rad), 0, np.cos(-theta2_rad), 0],
                    [0, 0, 0, 1]])
        Tx_L2 = np.array([[1, 0, 0, L2],
                [0, 1, 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1]])
        Ry_theta3 = np.array([[np.cos(theta3_rad), 0, np.sin(theta3_rad), 0],
                    [0, 1, 0, 0],
                    [-np.sin(theta3_rad), 0, np.cos(theta3_rad), 0],
                    [0, 0, 0, 1]])
        Tx_L3 = np.array([[1, 0, 0, L3],
                [0, 1, 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1]])
        origin = np.array([[0],
                [0],
                [0],
                [1]])
        transform_toe = Rz_theta1 @ Tx_L1 @ Ry_theta2 @ Tx_L2 @ Ry_theta3 @ Tx_L3
        transform_knee = Rz_theta1 @ Tx_L1 @ Ry_theta2 @ Tx_L2
        transform_femur = Rz_theta1 @ Tx_L1
        output_toe = transform_toe @ origin
        output_knee = transform_knee @ origin
        output_femur = transform_femur @ origin
        #print(output_toe[0:2,0])
        toe[i,:] = np.transpose(output_toe[0:3,0])
        knee[i,:] = np.transpose(output_knee[0:3,0])
        femur[i,:] = np.transpose(output_femur[0:3,0])

    return toe, knee, femur

x, y, z = fk_matrix(theta1,theta2,theta3)
#print(x)
#print(y)
#print(z)

# plot graph on a fixed point: use the third element

# function to get list of r & z, input are numbers
def calculate_for_plot(theta1,theta2, theta3):
    toe, knee, femur = fk_matrix([theta1],[theta2],[theta3])
    r = np.zeros(4)
    z = np.zeros(4)
    #print(toe)
    #print(knee)
    #print(femur)

    for i,lst in enumerate([femur[0,:], knee[0,:], toe[0,:]]):
        r[i+1] = np.sqrt(lst[0]**2 + lst[1]**2) * np.sign(lst[0])
        z[i+1] = lst[2]
    return r, z


# plot default value
r, z = calculate_for_plot(0, 30, 105)

# plot 1
fig, ax = plt.subplots()
line, = ax.plot(r,z,'o-')
ax.set_aspect('equal')
ax.set_xlim(-100, 300)
ax.set_ylim(-200, 200)

# create axes for slider; create slider
axtheta2 = fig.add_axes((0.05, 0.5, 0.0225, 0.3))
axtheta3 = fig.add_axes((0.05, 0.1, 0.0225, 0.3))
theta2Slider = Slider(axtheta2, label='theta2',valmin=-75,valmax=75,orientation='vertical')
theta3Slider = Slider(axtheta3, label='theta3',valmin=15,valmax=165,orientation='vertical')
# update data based on slider
def update(val):
    value1 = theta2Slider.val
    value2 = theta3Slider.val
    r_updated, z_updated = calculate_for_plot(0, value1, value2)
    line.set_data(r_updated, z_updated)
    fig.canvas.draw_idle()

theta2Slider.on_changed(update)
theta3Slider.on_changed(update)

# plot 2 for all toe poses
fig1, ax1 = plt.subplots()
range_theta2 = list(range(-75, 76))
range_theta3 = list(range(15, 166))
r_2= np.zeros((len(range_theta2), len(range_theta3)))
z_2 = np.zeros((len(range_theta2), len(range_theta3)))
for i in range(len(range_theta2)):
    for j in range(len(range_theta3)):
        r, z= calculate_for_plot(0, range_theta2[i], range_theta3[j])
        r_2[i, j] = r[-1]
        z_2[i, j] = z[-1]

ax1.scatter(r_2.flatten().tolist(),z_2.flatten().tolist())



plt.show()
