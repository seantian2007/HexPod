import constants
import numpy as np
from .gaits import GAITS, leg_phase

class Walker:
    def __init__(self, gait = "tripod", T = 2.5, h = 30):
        self.t = 0
        self.p0 = constants.F_DEFAULT.copy()
        self.p = constants.F_DEFAULT.copy()
        self.lift = np.zeros((6, 3))
        self.was_stance = np.ones(6, dtype=bool)
        self.gait = gait
        self.T = T
        self.h = h
        self.beta = GAITS[self.gait][0]

    ## INPUT:
    # vx, vy : speed of body mm/s（x front，y left）
    # w: rotational speed of body °/s（CCW positive）
    ## OUTPUT:
    # feet: (6, 3) new feet pose, body coords
    def step(self, vx, vy, w, dt=0.02):
        w_rad = np.radians(w)
        k = self.beta * self.T / 2

        for i in range(6):
            (in_stance, s) = leg_phase(i, self.t, self.T, self.gait)
            x_0, y_0, z_0 = self.p0[i, 0].copy(), self.p0[i, 1].copy(), self.p0[i, 2].copy()   # ❌ 支撑相要从“当前位置” self.p[i] 积分，这里改成 p0 后支撑脚每帧都被拉回中性点、根本不往后退。
                                                                                                          #    支撑相用 x, y = self.p[i, 0], self.p[i, 1]；摆动相里的 AEP_x、AEP_y 和 z 用 p0 是对的
            if in_stance == True:
                xc, yc = self.p[i, 0], self.p[i, 1]
                x = xc - (vx - w_rad * yc) * dt
                y = yc - (vy + w_rad * xc) * dt
                self.p[i, 0] = x
                self.p[i, 1] = y
                self.p[i, 2] = z_0
            else:
                if self.was_stance[i] == True:
                    self.lift[i, :] = self.p[i, :]
                AEP_x = x_0 + k * (vx - w_rad * y_0)
                AEP_y = y_0 + k * (vy + w_rad * x_0)
                c = s - np.sin(2 * np.pi * s) / (2 * np.pi)
                x = self.lift[i, 0] + c * (AEP_x - self.lift[i, 0])
                y = self.lift[i, 1] + c * (AEP_y - self.lift[i, 1])
                z = z_0 + self.h * (1 - np.cos(2 * np.pi * s)) / 2
                self.p[i, :] = np.array([x, y, z])

            self.was_stance[i] = in_stance

        self.t += dt
        return self.p.copy()


        