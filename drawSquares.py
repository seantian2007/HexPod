import numpy as np
from IKTest import ik
import time
import constants
import serial
from AngleToPulse import angleToPulse

# define the coords of the corners here
corners = np.array([
    [162 - 20, 20, -89.5],
    [162 + 20, 20, -89.5],
    [162 + 20, -20, 89.5],
    [162 - 20, -20, -89.5]
])

# rate in Hz, should put in constant file
rate = 50

# function that takes in coords of four corners 
# and output arrays of thetas to follow
# input: (4, 3) np array
def getTheta(corners):
    # define lists to store servo values during drawing
    theta1_s = np.array([ik(corners[0, 0], corners[0, 1], corners[0, 2])[0]])
    theta2_s = np.array([ik(corners[0, 0], corners[0, 1], corners[0, 2])[1]])
    theta3_s = np.array([ik(corners[0, 0], corners[0, 1], corners[0, 2])[2]])
    time_s = np.array([0])

    origin_time_ns = time.monotonic_ns()
    for i in range(4):
        dur = abs(corners[0, 1] - corners[2, 1]) / constants.MAX_LINEAR_SPEED # in seconds, should give 40 / 40
        u = 0

        start_pos = corners[i, :]
        if i == 3:
            target_pos = corners[0, :]
        else:
            target_pos = corners[i + 1, :]

        #start_time_ns = time.monotonic_ns()
        
        N = round(dur * rate)
        for k in range(N +1):
            # now_time_ns = time.monotonic_ns()
            # elapsed_time_s = (now_time_ns - start_time_ns) * 1e-9
            #u = min(elapsed_time_s/dur, 1)
            u = k / N
            pos = start_pos + u * (target_pos - start_pos)
            pos[2] = -89.5
            #print(u)
            #print(pos)
            #print(ik(pos[0], pos[1], pos[2]))
            cmd_theta1 = ik(pos[0], pos[1], pos[2])[0]
            cmd_theta2 = ik(pos[0], pos[1], pos[2])[1]
            cmd_theta3 = ik(pos[0], pos[1], pos[2])[2]
            theta1_s = np.append(theta1_s, cmd_theta1)
            theta2_s = np.append(theta2_s, cmd_theta2)
            theta3_s = np.append(theta3_s, cmd_theta3)
            time_s = np.append(time_s, time.monotonic_ns() - origin_time_ns)

    return theta1_s, theta2_s, theta3_s

ser = serial.Serial('/dev/cu.usbserial-120', 115200)
time.sleep(2) # Wait for Arduino initialization
print("initialize completed")

theta1, theta2, theta3 = getTheta(corners)
print("calculation completed")

t0 = time.monotonic()
for i in range(len(theta1)):
    cmd_theta1 = theta1[i]
    cmd_theta2 = theta2[i]
    cmd_theta3 = theta3[i]

    coxaPulse = angleToPulse(cmd_theta1, "TestLeg", "coxa")
    femurPulse = angleToPulse(cmd_theta2, "TestLeg", "femur")
    tibiaPulse = angleToPulse(cmd_theta3, "TestLeg", "tibia")
    if coxaPulse == None or femurPulse == None or tibiaPulse == None:
        print("input values out of range")
        continue

    message = f"{round(coxaPulse)},{round(femurPulse)},{round(tibiaPulse)}\n" # servo only takes in int for input

    # wait
    time.sleep(max(0, t0 + i / rate - time.monotonic()))
    ser.write(message.encode('utf-8'))


    if ser.in_waiting > 0:
        line = ser.readline().decode('utf-8').rstrip() # Read, decode bytes, strip whitespace
        if line == "Done":
            print("Done")
        elif line == "ERR":
            print("ERR")
    # if line == "Done":
    #     print("Action comleted")
    #     wantAgain = input("Do you want to perform another move? (y/n)")
    #     if wantAgain == "y":
    #         repeat = True
    #     elif wantAgain == "n":
    #         repeat = False
    #     else:
    #         repeat = False
    #         print("input not valid, exiting...")
    # elif line == "ERR":
    #     print("Input values from python ERR, exiting...")
    #     repeat = False
ser.close()



