import serial
import time
import csv
import numpy as np
from AngleToPulse import angleToPulse

repeat = True
ser = serial.Serial('/dev/cu.usbserial-120', 115200)
time.sleep(2) # Wait for Arduino initialization

while repeat == True:
    theta1 = int(input("What's the value for theta1 in degrees: "))
    theta2 = int(input("What's the value for theta2 in degrees: "))
    theta3 = int(input("What's the value for theta3 in degrees: "))

    coxaPulse = angleToPulse(theta1, "TestLeg", "coxa")
    femurPulse = angleToPulse(theta2, "TestLeg", "femur")
    tibiaPulse = angleToPulse(theta3, "TestLeg", "tibia")
    if coxaPulse == None or femurPulse == None or tibiaPulse == None:
        print("input values out of range")
        continue

    message = f"{round(coxaPulse)},{round(femurPulse)},{round(tibiaPulse)}\n" # servo only takes in int for input

    ser.write(message.encode('utf-8'))

    conpleted = False
    while not ser.in_waiting > 0:
        print("Servos in action!")
    line = ser.readline().decode('utf-8').rstrip() # Read, decode bytes, strip whitespace
    if line == "Done":
        print("Action comleted")
        wantAgain = input("Do you want to perform another move? (y/n)")
        if wantAgain == "y":
            repeat = True
        elif wantAgain == "n":
            repeat = False
        else:
            repeat = False
            print("input not valid, exiting...")
    elif line == "ERR":
        print("Input values from python ERR, exiting...")
        repeat = False
ser.close()


