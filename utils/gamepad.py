import os
os.environ["SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS"] = "1"
import pygame
import numpy as np
import time
import sys

# Axis / button numbers. Change these when switching controller, computer or connection.
# To find them: python3 -m utils.gamepad --map
AXES = dict(lx=0, ly=1,          # left stick x (right +), y (down +)
            rx=2, ry=3,          # right stick
            lt=4, rt=5)          # triggers
TRIGGER_REST = -1.0              # trigger reading when released (-1 on Mac + Xbox; set 0.0 if --map shows 0)
BUTTONS = dict(reset=0,          # A
               quit=1,           # B
               dance=2,          # X
               pose=3)           # Y
DPAD = 'hat'                     # 'hat' = hat 0; or dict(up=.., down=.., left=.., right=..) if the D-pad is buttons


class _Pad:
    """Shared by GamePad and KeyboardPad: deadzone, combined limit, rate limit, press detection.
    Subclasses implement _raw() -> (axes: dict, buttons: dict) using the AXES / BUTTONS names,
    plus gait_prev / gait_next in buttons."""

    def __init__(self, v_max=40, w_max=15, deadzone=0.1, accel=100):
        self.deadzone = deadzone
        self.v_max = v_max
        self.w_max = w_max
        self.accel = accel
        self.last_Joy = np.zeros(3)
        self.axes = {k: 0.0 for k in AXES}
        self.btn = {}
        self.btn_prev = {}

    def _poll(self):
        """Read raw inputs once per frame and keep last frame's buttons."""
        self.btn_prev = self.btn
        self.axes, self.btn = self._raw()

    def sticks(self):
        """Sticks after deadzone, -1..1, up/right positive."""
        a = self.axes
        raw = np.array([a['lx'], -a['ly'], a['rx'], -a['ry']])
        raw[np.abs(raw) < self.deadzone] = 0
        return raw                                           # (lx, ly, rx, ry)

    def triggers(self):
        """Left and right trigger, 0 = released, 1 = fully pressed."""
        return self.axes['lt'], self.axes['rt']

    def pressed(self, name):
        """True only on the frame the button goes down."""
        return bool(self.btn.get(name, 0)) and not bool(self.btn_prev.get(name, 0))

    def quit_pressed(self):
        return bool(self.btn.get('quit', 0))

    def read(self, dt=0.02, enabled=True):
        """Return (vx, vy, w). enabled=False ramps the command to 0 at the accel limit."""
        self._poll()
        lx, ly, rx, ry = self.sticks()
        cmd = np.array([ly * self.v_max, -lx * self.v_max, -rx * self.w_max])  # vx, vy, w
        if not enabled:
            cmd[:] = 0

        lim = np.hypot(cmd[0], cmd[1]) / self.v_max + abs(cmd[2]) / self.w_max
        if lim > 1:
            cmd /= lim

        step = self.accel * dt * np.array([1, 1, self.w_max / self.v_max])
        cmd = self.last_Joy + np.clip(cmd - self.last_Joy, -step, step)
        self.last_Joy = cmd
        return tuple(cmd)


class GamePad(_Pad):
    def __init__(self, v_max=40, w_max=15, deadzone=0.1, accel=100):
        super().__init__(v_max, w_max, deadzone, accel)
        pygame.joystick.init()
        pygame.init()
        if (pygame.joystick.get_count()>0):
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
        else:
            self.joystick = None
            raise RuntimeError("No joystick detected")
        # SDL may read an untouched trigger as half-pressed; ignore each trigger until it reads released once
        self.trigger_armed = {'lt': False, 'rt': False}

    def _raw(self):
        pygame.event.pump()
        j = self.joystick
        axes = {k: j.get_axis(n) for k, n in AXES.items() if n < j.get_numaxes()}
        for k in ('lx', 'ly', 'rx', 'ry', 'lt', 'rt'):
            axes.setdefault(k, TRIGGER_REST if k in ('lt', 'rt') else 0.0)
        for k in ('lt', 'rt'):                                # triggers -> 0..1
            v = axes[k]
            if abs(v - TRIGGER_REST) < 0.05:
                self.trigger_armed[k] = True
            axes[k] = float(np.clip((v - TRIGGER_REST) / (1 - TRIGGER_REST), 0, 1)) if self.trigger_armed[k] else 0.0
        btn = {k: j.get_button(n) for k, n in BUTTONS.items() if n < j.get_numbuttons()}
        if DPAD == 'hat':
            hx, hy = j.get_hat(0) if j.get_numhats() > 0 else (0, 0)
            btn['gait_prev'], btn['gait_next'] = int(hx < 0), int(hx > 0)
        else:
            nb = j.get_numbuttons()
            btn['gait_prev'] = j.get_button(DPAD['left']) if DPAD['left'] < nb else 0
            btn['gait_next'] = j.get_button(DPAD['right']) if DPAD['right'] < nb else 0
        return axes, btn


class KeyboardPad(_Pad):
    """Keyboard stand-in (SIM window must be focused):
       W/S A/D = left stick   Q/E = turn   I/K J/L = right stick (pose mode)
       R/F = raise/lower   P = pose mode   X = dance   Z = reset   [ ] = gait   Esc = quit"""

    def __init__(self, v_max=40, w_max=15, deadzone=0.1, accel=100):
        super().__init__(v_max, w_max, deadzone, accel)
        pygame.init()

    def _raw(self):
        pygame.event.pump()
        k = pygame.key.get_pressed()
        axes = dict(lx=k[pygame.K_d] - k[pygame.K_a], ly=k[pygame.K_s] - k[pygame.K_w],
                    rx=(k[pygame.K_e] or k[pygame.K_l]) - (k[pygame.K_q] or k[pygame.K_j]),
                    ry=k[pygame.K_k] - k[pygame.K_i],
                    lt=float(k[pygame.K_f]), rt=float(k[pygame.K_r]))
        btn = dict(quit=k[pygame.K_ESCAPE], pose=k[pygame.K_p], dance=k[pygame.K_x], reset=k[pygame.K_z],
                   gait_prev=k[pygame.K_LEFTBRACKET], gait_next=k[pygame.K_RIGHTBRACKET])
        return axes, btn


def _map_tool():
    """python3 -m utils.gamepad --map : print the number of every button / axis / hat you touch."""
    pygame.init()
    pygame.joystick.init()
    if pygame.joystick.get_count() == 0:
        print("没检测到手柄")
        return
    j = pygame.joystick.Joystick(0)
    j.init()
    print(f"{j.get_name()}: {j.get_numaxes()} axes, {j.get_numbuttons()} buttons, {j.get_numhats()} hats")
    print("先什么都别碰，记下扳机松开时的读数；然后挨个按键、推摇杆、按扳机和十字键。Ctrl-C 退出。")
    pygame.event.pump()
    print("rest axes:", [round(j.get_axis(k), 2) for k in range(j.get_numaxes())])
    last_b, last_h = set(), None
    last_a = [j.get_axis(k) for k in range(j.get_numaxes())]
    while True:
        pygame.event.pump()
        b = {n for n in range(j.get_numbuttons()) if j.get_button(n)}
        if b != last_b:
            for n in b - last_b:
                print(f"button {n} pressed")
            last_b = b
        h = [j.get_hat(n) for n in range(j.get_numhats())]
        if h != last_h:
            print("hats:", h)
            last_h = h
        a = [j.get_axis(k) for k in range(j.get_numaxes())]
        for k in range(len(a)):
            if abs(a[k] - last_a[k]) > 0.5:
                print(f"axis {k}: {a[k]:+.2f}")
                last_a[k] = a[k]
        time.sleep(0.02)


if __name__ == "__main__":
    if '--map' in sys.argv:
        _map_tool()
    else:
        joy = GamePad()
        while True:
            time.sleep(0.1)
            print(joy.read(dt=0.1), joy.triggers(), {k: v for k, v in joy.btn.items() if v})
