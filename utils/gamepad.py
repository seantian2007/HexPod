import os
os.environ["SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS"] = "1"
import pygame
import numpy as np
import time

class GamePad:
    def __init__(self, v_max=40, w_max=15, deadzone=0.1, accel=100):
        pygame.joystick.init()
        pygame.init()
        #pygame.display.set_mode((1, 1))
        if (pygame.joystick.get_count()>0):
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
        else:
            self.joystick = None
            raise RuntimeError("No joystick detected")
        self.deadzone = deadzone
        self.v_max = v_max
        self.w_max = w_max
        self.accel = accel
        self.last_Joy = np.zeros(3)



    def read(self, dt=0.02):
        pygame.event.pump()
        raw = np.array([self.joystick.get_axis(k) for k in (0, 1, 2)])   # 左x, 左y, 右x（编号先确认）
        raw[np.abs(raw) < self.deadzone] = 0
        cmd = np.array([-raw[1] * self.v_max, -raw[0] * self.v_max, -raw[2] * self.w_max])  # vx, vy, w

        lim = np.hypot(cmd[0], cmd[1]) / self.v_max + abs(cmd[2]) / self.w_max
        if lim > 1:
            cmd /= lim

        step = self.accel * dt * np.array([1, 1, self.w_max / self.v_max])
        cmd = self.last_Joy + np.clip(cmd - self.last_Joy, -step, step)
        self.last_Joy = cmd
        return tuple(cmd)

    def quit_pressed(self):
        return self.joystick.get_button(1)

if __name__ == "__main__":
    joy = GamePad()
    while True:
        time.sleep(0.1)
        print(joy.read(dt=0.1))
            
