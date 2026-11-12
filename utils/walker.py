import constants
import numpy as np
from .gaits import GAITS, leg_phase

# below these the command counts as zero
EPS_V = 0.5     # mm/s
EPS_W = 0.2     # deg/s


class Walker:
    # stopped : all feet down at p0, phase frozen
    # idle    : time (s) the command has been zero; after idle_time, legs settle back to p0
    # settled : legs that have landed at p0 while settling
    # hold    : legs mid-swing at start-up, kept in stance until their phase reaches stance
    def __init__(self, gait = "tripod", T = 2.5, h = 30, idle_time = 0.3):
        self.t = 0
        self.p0 = constants.F_DEFAULT.copy()
        self.p = constants.F_DEFAULT.copy()
        self.lift = np.zeros((6, 3))
        self.was_stance = np.ones(6, dtype=bool)
        self.gait = gait
        self.T = T
        self.h = h
        self.beta = GAITS[self.gait][0]

        self.idle_time = idle_time
        self.idle = 0.0
        self.stopped = True
        self.settled = np.zeros(6, dtype=bool)
        self.hold = np.zeros(6, dtype=bool)
        self._start_hold()

    # switch gait; only allowed while stopped
    def set_gait(self, gait, T):
        if not self.stopped:
            return False
        self.gait, self.T = gait, T
        self.beta = GAITS[gait][0]
        delta = GAITS[gait][1]
        # start at the moment R1 begins its swing
        self.t = (delta[0] + self.beta) * T
        self._start_hold()
        return True

    def _start_hold(self):
        """Prepare to start walking: shift t so the first swinging leg starts at s = 0,
        and hold other mid-swing legs until they reach stance."""
        phases = [leg_phase(i, self.t, self.T, self.gait) for i in range(6)]
        swing_s = [s for st, s in phases if not st]
        if swing_s:
            self.t -= min(swing_s) * (1 - self.beta) * self.T
        one_frame = 0.02 / ((1 - self.beta) * self.T)
        for i in range(6):
            in_stance, s = leg_phase(i, self.t, self.T, self.gait)
            self.hold[i] = (not in_stance) and s > one_frame

    ## INPUT:
    # vx, vy : speed of body mm/s (x front, y left)
    # w: rotational speed of body deg/s (CCW positive)
    ## OUTPUT:
    # feet: (6, 3) new feet pose, body coords
    def step(self, vx, vy, w, dt=0.02):
        # auto stop / start
        moving = abs(vx) > EPS_V or abs(vy) > EPS_V or abs(w) > EPS_W
        if moving:
            self.idle = 0.0
            if self.stopped:
                self.stopped = False
                self._start_hold()
            elif self.settled.any():                    # restarted while settling: hold settled legs that are mid-swing
                for i in np.where(self.settled)[0]:
                    in_stance, _ = leg_phase(i, self.t, self.T, self.gait)
                    self.hold[i] = self.hold[i] or not in_stance
            self.settled[:] = False
        else:
            self.idle += dt
        if self.stopped:
            return self.p.copy()
        settling = self.idle >= self.idle_time

        w_rad = np.radians(w)
        k = self.beta * self.T / 2

        for i in range(6):
            (in_stance, s) = leg_phase(i, self.t, self.T, self.gait)
            if self.hold[i]:                            # held legs stay in stance until their phase does
                if in_stance:
                    self.hold[i] = False
                else:
                    in_stance = True
            if settling and self.settled[i]:            # settled legs don't lift again
                in_stance = True
            x_0, y_0, z_0 = self.p0[i, 0], self.p0[i, 1], self.p0[i, 2]
            if in_stance == True:
                if settling and not self.was_stance[i]:  # swing leg just landed at p0
                    self.settled[i] = True
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

        # all legs settled at p0 -> stop
        if settling and self.settled.all():
            self.stopped = True
            self.p[:, 2] = self.p0[:, 2]
            self.was_stance[:] = True
        return self.p.copy()
