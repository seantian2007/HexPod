import time
import numpy as np
from utils.link import Link
from utils.planner import make_plan_feet
from utils.feet_traj import feet_straight

# ---- Parameters. First run: robot lifted off the ground, S = 0 (step in place), small h ----
GAIT, T, S, H = 'tripod', 2.5, 0, 10
CYCLES = 4                       # whole cycles, so the last frame has (almost) all feet down
HOME = np.array([0, 30, 105] * 6)

# Plan everything first: if any frame is out of range or too fast, this raises before anything moves
feet_fn = lambda t: feet_straight(t, T=T, S=S, h=H, gait=GAIT)
times, thetas = make_plan_feet(feet_fn, duration=CYCLES * T)

link = Link()
try:
    link.move_to(HOME, 1)        # pose unknown at start -> sends HOME directly
    time.sleep(2)                # firmware enables the 18 servos one by one (~1 s)
    link.play(thetas)            # eases into frame 0 over 1 s, then plays at 50 Hz
finally:
    link.move_to(HOME, 1.5)      # also runs after Ctrl-C or an error
    link.close()
