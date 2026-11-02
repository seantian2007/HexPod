import numpy as np
import time
import matplotlib.pyplot as plt

# define length in mm
L1 = 62
L2 = 76
L3 = 132

# define max speed for toe (mm/s)
MAX_SPEED = 40

# input: target point in mm
# output: theta1 - 3 in degrees
def ik(x,y,z):
    theta1 = np.rad2deg(np.atan2(y, x)) 
    r = np.sqrt(x**2 + y**2)

  
    # here if theta1 is within [-45, 45] it's fine; if not, we make r a negative number
    if theta1 < -90:
        theta1 += 180
        r *= -1
    elif theta1 > 90:
        theta1 -= 180
        r *= -1


    # if abs of theta1 out of bound, return no sol
    if not (theta1 <= 45 + 1e-9 and theta1 >= -45 - 1e-9):
        return None

    u = r - L1
    D = np.sqrt(u**2 + z**2)

    # before calculating for theta3, we check if the calculated D will guarentee a solution
    if D > L2 + L3 or D < L3 - L2:
        return None
    
    # use law of cosine to get theta3; we only want the positive solution here
    theta3 = np.rad2deg(np.arccos((D**2 - L2**2 - L3**2)/(2 * L2 * L3)))

    # check if theta3 is within [15, 165]; if not, return no solution
    if not (theta3 >= 15 - 1e-8 and theta3 <= 165 + 1e-8):
        return None

    # calculate for theta2
    alpha = np.atan2(z, u)
    beta = np.atan2(L3 * np.sin(np.deg2rad(theta3)), L2 + L3 * np.cos(np.deg2rad(theta3)))
    theta2 = np.rad2deg(alpha + beta) # we only want the knee-up solution here

    # bound theta2 in [-180, 180]
    if theta2 > 180:
        theta2 -= 360
    elif theta2 < -180:
        theta2 += 360
    
    # check if theta2 is within [-75, 75]
    if not (theta2 >= -75 - 1e-9 and theta2 <= 75 + 1e-9):
        return None

    return (theta1.item(), theta2.item(), theta3.item())

#print(ik(143.75549668, 202, -89.5))

if __name__ == "__main__":

    # use toe to draw squares

    # define the four corners
    corners = np.array([
        [162 - 20, 20, -89.5],
        [162 + 20, 20, -89.5],
        [162 + 20, -20, 89.5],
        [162 - 20, -20, -89.5]
    ])

    # define lists to store servo values during drawing
    theta1_s = np.array([ik(corners[0, 0], corners[0, 1], corners[0, 2])[0]])
    theta2_s = np.array([ik(corners[0, 0], corners[0, 1], corners[0, 2])[1]])
    theta3_s = np.array([ik(corners[0, 0], corners[0, 1], corners[0, 2])[2]])
    time_s = np.array([0])

    def get_cur_theta():
        return np.array([theta1_s[-1], theta2_s[-1], theta3_s[-1]])

    origin_time_ns = time.monotonic_ns()
    for i in range(4):
        dur = 40 / MAX_SPEED # in seconds
        u = 0

        start_pos = corners[i, :]
        if i == 3:
            target_pos = corners[0, :]
        else:
            target_pos = corners[i + 1, :]

        start_time_ns = time.monotonic_ns()
        while u < 1:
            now_time_ns = time.monotonic_ns()
            elapsed_time_s = (now_time_ns - start_time_ns) * 1e-9
            u = min(elapsed_time_s/dur, 1)

            pos = start_pos + u * (target_pos - start_pos)
            pos[2] = -89.5
            #print(u)
            print(pos)
            #print(ik(pos[0], pos[1], pos[2]))
            cmd_theta1 = ik(pos[0], pos[1], pos[2])[0]
            cmd_theta2 = ik(pos[0], pos[1], pos[2])[1]
            cmd_theta3 = ik(pos[0], pos[1], pos[2])[2]
            theta1_s = np.append(theta1_s, cmd_theta1)
            theta2_s = np.append(theta2_s, cmd_theta2)
            theta3_s = np.append(theta3_s, cmd_theta3)
            time_s = np.append(time_s, time.monotonic_ns() - origin_time_ns)

    fig, ax = plt.subplots()
    ax.plot(time_s, theta1_s, 'k', label = 'theta1')
    ax.plot(time_s, theta2_s, 'b', label = 'theta2')
    ax.plot(time_s, theta3_s, 'r', label = 'theta3')
    ax.legend()
    plt.show()