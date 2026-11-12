import serial
import time
import numpy as np
from .AngleToPulse import angleToPulse


class Link: 
    def __init__(self, baud=115200):
        self.ser = serial.Serial()
        self.ser.port = '/dev/cu.usbserial-0001'
        self.ser.baudrate = baud
        self.ser.dtr = False
        self.ser.rts = False
        self.ser.open()
        time.sleep(2) # Wait for esp initialization
        self.latest_angle = None
        self.rate = 50 #Hz

    def send_angles(self, angles):
        cmd_theta = angles.copy()
        cmd_pulse = angleToPulse(cmd_theta)
        self.latest_angle = cmd_theta.copy()
        message = ",".join(np.round(cmd_pulse).astype(int).astype(str)) + "\n"
        self.ser.write(message.encode("utf-8"))

    # Dont's use this for now; missing the code to update latest angle/pulse
    def send_pulses(self, pulse):
        cmd_pulse = pulse.copy()
        message = ",".join(np.round(cmd_pulse).astype(int).astype(str)) + "\n"
        self.ser.write(message.encode("utf-8"))

    def move_to(self, target_angle, sec):
        #HOME_ANGLE = np.array([0, 30, 105] * 6)
        if self.latest_angle is None:
            self.send_angles(target_angle)
        else:
            N = int(round(sec * self.rate))
            t0 = time.perf_counter()
            start = self.latest_angle.copy()
            for i in range(N+1):
                k = i/N
                cmd_angle = start + k * (target_angle - start)
                while time.perf_counter() < t0 + i/self.rate:
                    continue
                self.send_angles(cmd_angle)

    # INPUT: thetas should be a n by 18 matrix
    def play(self, thetas):
        i = 0
        self.move_to(thetas[0, :], 1)
        t0 = time.perf_counter()
        while i < len(thetas[:, 0]):
            cmd_angle = thetas[i, :]
            while time.perf_counter() < t0 + i / self.rate:
                continue
 
            self.send_angles(cmd_angle)
            i += 1

    def close(self):
        self.ser.close()


