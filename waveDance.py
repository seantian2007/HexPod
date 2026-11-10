from utils.planner import make_plan
from utils.dancesFunc import wave_dance
from utils.AngleToPulse import angleToPulse
import time
import serial
import numpy as np

ser = serial.Serial()
ser.port = '/dev/cu.usbserial-0001'
ser.baudrate = 115200
ser.dtr = False
ser.rts = False
ser.open()
time.sleep(2) # Wait for esp initialization (do we need this?)

times, poses, thetas = make_plan(wave_dance, 30)

print(len(times))

i = 0

#ser.write(b'1480,1913,1717,1520,1823,1687,1410,1813,1697,1450,1247,1343,1490,1137,1303,1540,1167,1333\n')
ser.write(b'1480, 1580, 1550, 1520, 1490, 1520, 1410, 1480, 1530, 1450, 1580, 1510, 1490, 1470, 1470, 1540, 1500, 1500\n')

time.sleep(1.5)

while i < len(times):
    cmd_theta = thetas[i, :]
    cmd_pulse = angleToPulse(cmd_theta)
    message = ",".join(np.round(cmd_pulse).astype(int).astype(str)) + "\n"
    ser.write(message.encode("utf-8"))
    time.sleep(0.01)
    i += 1