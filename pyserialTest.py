import serial
import time
import csv
import numpy as np

file_path = "ServoAngleTest.csv"
header = ["PulseWidth", "Angle"]

num_exp = int((2500 - 500) / 100 + 1) # should return 21
data = np.zeros((num_exp,2))

# fill the first column
data[:,0] = list(range(500, 2600, 100))

ser = serial.Serial('/dev/cu.usbserial-120', 115200)
time.sleep(2) # Wait for Arduino initialization

# define iterable
i = 0
while i < int(num_exp):
    # Send '1' to turn the LED on, meaning experiment has started
    ser.write(b'1') 
    time.sleep(1)
    if ser.in_waiting > 0: # Check if data is available
        line = ser.readline().decode('utf-8').rstrip() # Read, decode bytes, strip whitespace
        if line == "Done; wait for next":
            value = input("Please put in the protractor value: ")
            data[i,1] = value
            i += 1
ser.close() # Always close the port when done

with open(file_path, mode="w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)

    # Write the header row
    writer.writerow(header)

    # Write multiple data rows at once
    writer.writerows(data)
