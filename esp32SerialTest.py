import serial
import time
import numpy as np

ser = serial.Serial('/dev/cu.usbserial-0001', 115200)
time.sleep(2) # Wait for Arduino initialization

# define iterable
i = 0
while i <= 10 :
    # Send '1' to turn the LED on, meaning experiment has started
    #ser.write(b'1500') 
    time.sleep(1)
    if ser.in_waiting > 0: # Check if data is available
        line = ser.readline().decode('utf-8', errors='ignore').rstrip() # Read, decode bytes, strip whitespace
        print(line)
ser.close() # Always close the port when done
