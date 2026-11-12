from utils.gamepad import GamePad, KeyboardPad
from utils.walker import Walker
from utils.link import Link
from utils.planner import make_plan, solve_frame, check_rate
from utils.dancesFunc import wave_dance
from utils.gaits import GAITS
import numpy as np
import time
from utils.sim_view import LiveView

# Controls (button numbers live in utils/gamepad.py: AXES / BUTTONS / DPAD)
#   left stick        walk forward/back, strafe   (pose mode: pitch / roll)
#   right stick x     turn                        (pose mode: yaw)
#   RT / LT           raise / lower body
#   Y                 toggle pose mode (stops walking first)
#   X                 play wave dance (~12 s)
#   A                 reset pose and height
#   D-pad left/right  switch gait tripod / ripple / wave
#   B                 quit (real robot returns HOME)

SIM = False
LIMIT = 150        # joint speed limit, deg/s
GAIT, H, RATE = 'tripod', 30, 50
HOME = np.array([0, 30, 105] * 6, dtype=float)

# Per gait: period T, v_max = v * LIMIT (mm/s), w_max = w * LIMIT (deg/s)
GAIT_CFG = {
    'tripod': dict(T=2.5, v=0.38,  w=0.15),
    'ripple': dict(T=3.0, v=0.16,  w=0.075),
    'wave':   dict(T=6.0, v=0.075, w=0.035),
}
GAIT_ORDER = ['tripod', 'ripple', 'wave']
W_CAP = 21                                   # coxa range caps turning speed
Z_RANGE = (-15, 30)                          # body height range, mm
POSE_R, POSE_YAW = 10, 15                    # max roll/pitch and yaw in pose mode, deg
Z_RATE, ANG_RATE = 20, 15                    # pose change rates: mm/s, deg/s
Z_RATE_WALK = 8                              # slower height change while walking

if LIMIT > 150:
    print(f"⚠ LIMIT={LIMIT} 超过验证过的 150，v_max/w_max 是外推的，先架空试")


def v_scale(z):
    """Max walking speed shrinks when the body is raised or lowered."""
    return 1 - 0.0045 * max(z, 0) - 0.02 * max(-z, 0)


def apply_gait_limits(joy, view, gait, z):
    cfg, beta = GAIT_CFG[gait], GAITS[gait][0]
    joy.v_max = cfg['v'] * LIMIT * v_scale(z)
    joy.w_max = min(cfg['w'] * LIMIT, W_CAP)
    # keep AEP drift speed ~31 mm/s when the command changes mid-swing
    joy.accel = 31 / (beta * cfg['T'] / 2)
    if view is not None:
        view.v_max, view.w_max = joy.v_max, joy.w_max


def toward(cur, target, max_step):
    return cur + np.clip(target - cur, -max_step, max_step)


prev = HOME.copy()
joy = GamePad()                                           # use KeyboardPad() if no gamepad
gait = GAIT
walker = Walker(gait, GAIT_CFG[gait]['T'], H)
view = LiveView(rate=RATE, speed_limit=LIMIT) if SIM else None
apply_gait_limits(joy, view, gait, 0)

# precompute the dance (starts and ends at home)
_, _, dance_thetas = make_plan(wave_dance, 12, RATE)

pose = np.zeros(6)            # body pose (x, y, z, roll, pitch, yaw)
z_target = 0.0
mode = 'walk'                 # 'walk' / 'pose' / 'dance'
pending = None                # action to run once stopped: ('gait', name) or ('dance',)
dance_j = 0

log = {'t': [], 'wall': [], 'cmd': [], 'feet': [], 'stance': [], 'thetas': [], 'pose': [], 'mode': [], 'gait': []}
reason = ''
link = None
i = 0
dt = 1 / RATE

try:
    if not SIM:
        link = Link()
        link.move_to(HOME, 1)
        time.sleep(2)
    t0 = time.perf_counter()
    while True:
        while time.perf_counter() < t0 + i / RATE:
            continue

        # 1. read gamepad
        angles_home = np.all(np.abs(pose[3:]) < 0.2)
        walk_ok = (mode == 'walk') and pending is None and angles_home
        cmd = joy.read(dt=dt, enabled=walk_ok)
        if joy.quit_pressed():
            reason = 'quit'
            break

        # 2. buttons -> mode changes
        if mode != 'dance':
            if joy.pressed('pose'):
                mode = 'pose' if mode == 'walk' else 'walk'
            if joy.pressed('dance') and pending is None:
                mode, pending = 'walk', ('dance',)
            if joy.pressed('reset'):
                z_target = 0.0
                if mode == 'pose':
                    mode = 'walk'
            for name, step_ in (('gait_next', 1), ('gait_prev', -1)):
                if joy.pressed(name) and pending is None and mode == 'walk':
                    nxt = GAIT_ORDER[(GAIT_ORDER.index(gait) + step_) % len(GAIT_ORDER)]
                    pending = ('gait', nxt)
                    print(f"switching to {nxt} (waiting for all feet down)")

        # 3. body pose target
        lt, rt = joy.triggers()
        if mode != 'dance':
            z_target = float(np.clip(z_target + (rt - lt) * Z_RATE * dt, *Z_RANGE))
        target = np.zeros(6)
        target[2] = z_target
        if pending is not None and pending[0] == 'dance':
            target[2] = 0.0                                   # dance plan assumes height 0
        if mode == 'pose' and walker.stopped:
            lx, ly, rx, ry = joy.sticks()
            stick = np.array([lx, ly])
            n = np.linalg.norm(stick)
            if n > 1:
                stick /= n                                    # circular range
            target[3] = stick[0] * POSE_R                     # roll
            target[4] = -stick[1] * POSE_R                    # pitch (stick up = nose up)
            target[5] = -rx * POSE_YAW                        # yaw
        if mode != 'dance':
            pose[2] = toward(pose[2], target[2], (Z_RATE if walker.stopped else Z_RATE_WALK) * dt)
            pose[3:] = toward(pose[3:], target[3:], ANG_RATE * dt)
            apply_gait_limits(joy, view, gait, pose[2])

        # 4. once stopped: switch gait / start dance
        if pending is not None and walker.stopped:
            if pending[0] == 'gait':
                gait = pending[1]
                walker.set_gait(gait, GAIT_CFG[gait]['T'])
                apply_gait_limits(joy, view, gait, pose[2])
                print(f"gait = {gait}, T = {walker.T}, v_max = {joy.v_max:.0f} mm/s, w_max = {joy.w_max:.1f} deg/s")
                pending = None
            elif pending[0] == 'dance' and np.all(np.abs(pose) < 0.2):
                mode, dance_j, pending = 'dance', 0, None
                pose[:] = 0

        # 5. joint angles for this frame
        if mode == 'dance':
            feet = walker.p.copy()
            thetas = dance_thetas[dance_j]
            reason = check_rate(thetas, prev, RATE, LIMIT)
            if reason:
                thetas = None
            dance_j += 1
            if dance_j >= len(dance_thetas):
                mode = 'walk'
                z_target = 0.0
        else:
            feet = walker.step(cmd[0], cmd[1], cmd[2], dt) # (6, 3) matrix of cmd feet pose
            (thetas, reason) = solve_frame(feet, prev, RATE, LIMIT, pose)
        if thetas is None:
            print(f"At frame {i}, failure reason: {reason}")
            break
        else:
            if SIM == True:
                pass
            else:
                link.send_angles(thetas)

        log['t'].append(i / RATE)
        log['wall'].append(time.perf_counter() - t0)
        log['cmd'].append(cmd)
        log['feet'].append(feet)
        log['stance'].append(walker.was_stance.copy())
        log['thetas'].append(thetas)
        log['pose'].append(pose.copy())
        log['mode'].append(mode)
        log['gait'].append(gait)
        if view is not None:
            status = [f'gait {gait}  T={walker.T}  LIMIT={LIMIT}',
                      f'mode {mode.upper()}' + ('  (stopped)' if walker.stopped else '')
                      + (f'  -> {pending[0]} {pending[1] if len(pending) > 1 else ""}' if pending else ''),
                      f'z {pose[2]:+.0f}  roll {pose[3]:+.1f}  pitch {pose[4]:+.1f}  yaw {pose[5]:+.1f}']
            view.update(feet, walker.was_stance, cmd, thetas, prev, status)
            if view.closed:
                reason = 'quit'
                break

        prev = thetas
        i += 1
except KeyboardInterrupt:
    reason = 'quit (Ctrl-C)'
finally:
    if link is not None:
        link.move_to(HOME, 1)
        link.close()

    # save log; load with L = np.load('teleop_log.npz')
    np.savez('teleop_log.npz',
             t=np.array(log['t']),               # (N,)       planned time, s
             wall=np.array(log['wall']),         # (N,)       actual time, s
             cmd=np.array(log['cmd']),           # (N, 3)     vx, vy (mm/s), w (deg/s)
             feet=np.array(log['feet']),         # (N, 6, 3)  feet in body frame, mm
             stance=np.array(log['stance']),     # (N, 6)     True = on ground
             thetas=np.array(log['thetas']),     # (N, 18)    sent angles, deg
             pose=np.array(log['pose']),         # (N, 6)     body pose
             mode=np.array(log['mode']),         # (N,)       walk / pose / dance
             gaits=np.array(log['gait']),        # (N,)       gait per frame
             reason=reason, sim=SIM, gait=GAIT, T=GAIT_CFG[GAIT]['T'], H=H, rate=RATE, limit=LIMIT)
    print(f"saved teleop_log.npz: {len(log['t'])} frames, stop reason: {reason or 'none'}")
    print("回放: python3 -m utils.sim_view")
