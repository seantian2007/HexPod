"""Golden test: run the same scripted stick input through the Python code (utils/) and
the C++ code (sim_walk), frame by frame, and compare.

Run from code/firmware/test/:
    clang++ -std=c++17 -O2 -Wall -Wdouble-promotion sim_walk.cpp ../hexapod/src/core/*.cpp -o sim_walk
    python3 golden_walk.py
"""
import os
import subprocess
import sys
import types

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))           # code/
try:
    import pygame  # noqa: F401
except ImportError:                                           # gamepad.py imports pygame; not needed here
    sys.modules['pygame'] = types.ModuleType('pygame')

from utils.gamepad import _Pad                                # noqa: E402
from utils.walker import Walker                               # noqa: E402
from utils.gaits import GAITS                                 # noqa: E402
from utils.body_ik import body_ik                             # noqa: E402

DT, LIMIT, W_CAP = 0.02, 150, 21
GAIT_NAMES = ['tripod', 'ripple', 'wave']
GAIT_CFG = {'tripod': dict(T=2.5, v=0.38, w=0.15),           # = telop.py
            'ripple': dict(T=3.0, v=0.16, w=0.075),
            'wave':   dict(T=6.0, v=0.075, w=0.035)}


class ScriptPad(_Pad):
    """_Pad whose sticks come from the script instead of a controller."""
    def set(self, lx, ly, rx):
        self.next = dict(lx=lx, ly=-ly, rx=rx, ry=0.0, lt=0.0, rt=0.0)

    def _raw(self):
        return self.next, {}


def apply_gait_limits(joy, gait):                             # = telop.apply_gait_limits, z = 0
    cfg, beta = GAIT_CFG[gait], GAITS[gait][0]
    joy.v_max = cfg['v'] * LIMIT
    joy.w_max = min(cfg['w'] * LIMIT, W_CAP)
    joy.accel = 31 / (beta * cfg['T'] / 2)


def make_script(seed=0):
    rows = []
    def hold(n, lx=0.0, ly=0.0, rx=0.0, req=-1):
        rows.append((lx, ly, rx, req))
        rows.extend([(lx, ly, rx, -1)] * (n - 1))
    hold(50)                                   # stand still
    hold(250, ly=1)                            # forward, full stick
    hold(100)                                  # release -> settle
    hold(200, rx=1)                            # turn
    hold(150, lx=0.7, ly=0.7)                  # diagonal
    hold(300, req=1)                           # -> ripple
    hold(200, ly=1)
    hold(300, req=2)                           # -> wave
    hold(300, ly=0.6, rx=0.3)
    hold(300, req=0)                           # -> tripod
    rng = np.random.default_rng(seed)
    for _ in range(40):                        # random stick changes every 0.5 s
        lx, ly, rx = rng.uniform(-1, 1, 3)
        lx, ly, rx = [0.0 if abs(a) < 0.1 else float(a) for a in (lx, ly, rx)]
        hold(25, lx, ly, rx)
    hold(200)
    return rows


def run_python(rows):
    joy = ScriptPad()
    gait = 'tripod'
    apply_gait_limits(joy, gait)
    walker = Walker(gait, GAIT_CFG[gait]['T'], 30)
    pending = None
    out = []
    for lx, ly, rx, req in rows:
        joy.set(lx, ly, rx)
        cmd = joy.read(dt=DT, enabled=pending is None)
        if req >= 0 and pending is None:
            pending = GAIT_NAMES[req]
        if pending is not None and walker.stopped:
            gait = pending
            walker.set_gait(gait, GAIT_CFG[gait]['T'])
            apply_gait_limits(joy, gait)
            pending = None
        feet = walker.step(cmd[0], cmd[1], cmd[2], DT)
        thetas, status = body_ik(np.zeros(6), feet)
        ok = bool(np.all(status[:, 0]))
        out.append(np.concatenate([cmd, [walker.stopped], feet.flatten(), [ok],
                                   thetas.flatten() if ok else np.zeros(18)]))
    return np.array(out, dtype=float)


def run_cpp(rows):
    exe = os.path.join(HERE, 'sim_walk')
    text = ''.join(f'{lx} {ly} {rx} {req}\n' for lx, ly, rx, req in rows)
    res = subprocess.run([exe], input=text, capture_output=True, text=True, check=True)
    return np.loadtxt(res.stdout.splitlines())


if __name__ == '__main__':
    rows = make_script()
    py, cc = run_python(rows), run_cpp(rows)
    assert py.shape == cc.shape, (py.shape, cc.shape)
    d_cmd = np.abs(py[:, 0:3] - cc[:, 0:3]).max()
    d_stop = int((py[:, 3] != cc[:, 3]).sum())
    d_feet = np.abs(py[:, 4:22] - cc[:, 4:22]).max()
    d_ok = int((py[:, 22] != cc[:, 22]).sum())
    both = (py[:, 22] == 1) & (cc[:, 22] == 1)
    d_th = np.abs(py[both, 23:] - cc[both, 23:]).max()
    rate = np.abs(np.diff(py[both, 23:], axis=0)).max() / DT
    print(f'frames            {len(rows)}  ({len(rows) * DT:.0f} s)')
    print(f'cmd max diff      {d_cmd:.5f} mm/s or deg/s')
    print(f'stopped mismatch  {d_stop} frames')
    print(f'feet max diff     {d_feet:.5f} mm')
    print(f'ik ok mismatch    {d_ok} frames   (ik failed in {int((py[:, 22] == 0).sum())} Python frames)')
    print(f'theta max diff    {d_th:.5f} deg')
    print(f'peak joint speed  {rate:.1f} deg/s (Python)')
    passed = d_stop == 0 and d_ok == 0 and d_feet <= 0.05 and d_th <= 0.05
    print('PASS' if passed else 'FAIL')
