# import serial
# import time
# ser = serial.Serial('/dev/cu.usbserial-120', 115200, timeout=1)
# time.sleep(3)
# ser.reset_input_buffer()
# n = ser.write(b"1570,1460,1530\n")
# print("wrote", n, "bytes")
# print("reply:", repr(ser.readline()))
# ser.close()

# from utils.AngleToPulse import angleToPulse
# import numpy as np

# home = [0, 30, 105,   # R1
#         0, 30, 105,   # R2
#         0, 30, 105,   # R3
#         0, 30, 105,   # L1
#         0, 30, 105,   # L2
#         0, 30, 105]   # L3

# print(",".join(np.round(angleToPulse(home)).astype(int).astype(str)))


import os
os.environ["SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS"] = "1"
os.environ["SDL_JOYSTICK_MFI"] = "0"
import pygame, time
pygame.init()
print("count:", pygame.joystick.get_count())
for n in range(pygame.joystick.get_count()):
    j = pygame.joystick.Joystick(n); j.init()
    print(n, j.get_name(), "axes:", j.get_numaxes(), "buttons:", j.get_numbuttons())
j = pygame.joystick.Joystick(0)
while True:
    pygame.event.pump()
    print([round(j.get_axis(k), 2) for k in range(j.get_numaxes())])
    time.sleep(0.2)