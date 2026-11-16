"""Open-loop accuracy test (stage 6 milestones 4 and 5) on the stage 7/8 firmware.

Run from code/:
    python3 walk_test.py straight            # walk forward 300 mm, over WiFi
    python3 walk_test.py turn                # turn left 90 deg in place
    python3 walk_test.py straight --dist 500 / turn --angle -90
    python3 walk_test.py straight --speed 0.5 --gait ripple
    python3 walk_test.py straight --record   # also save the per-frame data (WiFi only)
    python3 walk_test.py straight --serial   # over USB, as in stage 7

The script stands the robot up (or unparks it), selects the gait, zeroes the odometry,
waits for you to line it up, sends a full stick for target / v_max seconds, waits until
the walker has stopped, and prints the odometry the ESP32 actually commanded. Then you
type in what you measured and it prints the error.
"""
import argparse
import math
import threading
import time

from utils.esp_link import add_link_args, open_link

RATE = 20
# v and w factors per gait (must match GAIT_CFG in command.cpp); x JOINT_SPEED_LIMIT 150
GAITS = {'tripod': (0.38, 0.15), 'ripple': (0.16, 0.075), 'wave': (0.075, 0.035)}


def get_status(link):
    """Ask the robot for 'status state=.. gait=.. recording=..' and return it as a dict."""
    for _ in range(3):                               # UDP: S could be lost, ask again
        link.send('S')
        try:
            line = link.wait_for('status ', 1.0)
        except TimeoutError:
            continue
        return dict(kv.split('=') for kv in line.split()[1:] if '=' in kv)
    raise SystemExit('the robot does not answer. WiFi joined? Robot powered?')


def get_ready(link, gait):
    """Bring the robot to RUN, unparked, in `gait`, with the odometry at zero."""
    st = get_status(link)
    if st['state'] in ('RELAXED', 'HOLD'):           # stand up / home first
        link.event('A')
        link.wait_for('state RUN', 15)
    elif st['state'] in ('STANDUP', 'HOMING'):       # already on its way
        link.wait_for('state RUN', 15)
    else:                                            # RUN: A unparks if parked, else does nothing
        link.event('A')
    st = get_status(link)
    names = list(GAITS)
    steps = (names.index(gait) - names.index(st['gait'])) % len(names)
    for _ in range(steps):                           # E,N steps tripod -> ripple -> wave
        link.event('N')
        link.wait_for('gait ', 5)
    link.event('Z')
    link.wait_for('odo reset', 2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('mode', choices=['straight', 'turn'])
    ap.add_argument('--dist', type=float, default=300, help='mm, straight mode')
    ap.add_argument('--angle', type=float, default=90, help='deg, CCW +, turn mode')
    ap.add_argument('--speed', type=float, default=1.0, help='stick fraction 0..1')
    ap.add_argument('--gait', choices=list(GAITS), default='tripod')
    ap.add_argument('--record', action='store_true', help='save per-frame data to logs/')
    add_link_args(ap)
    args = ap.parse_args()
    fv, fw = GAITS[args.gait]
    v_max, w_max = fv * 150, min(fw * 150, 21)

    link = open_link(args)
    done = threading.Event()

    def drive(lx, ly, rx, seconds):
        """Send the same sticks for `seconds` (or until done is set), at RATE Hz."""
        n = round(seconds * RATE)
        t0 = time.perf_counter()
        for i in range(n):
            if done.is_set():
                return
            while time.perf_counter() < t0 + i / RATE:
                time.sleep(0.002)
            drive.seq += 1
            link.send(f'C,{drive.seq},{lx:.3f},{ly:.3f},{rx:.3f}')
    drive.seq = 0

    try:
        if args.serial:
            link.wait_for('READY', 5)                # over USB, opening the port resets the ESP32
        get_ready(link, args.gait)
        input('\nPut the robot on the floor, line the plumb line up with the start mark, then press Enter ')
        if args.record:
            path = link.start_recording()
            if path:
                print(f'recording -> {path}')

        k = args.speed
        if args.mode == 'straight':
            seconds = abs(args.dist) / (k * v_max)
            drive(0, math.copysign(k, args.dist), 0, seconds)
        else:
            seconds = abs(args.angle) / (k * w_max)
            drive(0, 0, -math.copysign(k, args.angle), seconds)   # stick right = turn right (CW)
        print(f'{args.gait}, stick {k:.2f} held for {seconds:.2f} s, waiting for the walker to stop...')
        # keep sending zeros until we quit, so the ESP32 does not time out
        threading.Thread(target=drive, args=(0, 0, 0, 3600), daemon=True).start()
        line = link.wait_for('stopped: odo', 10)
        if link.recording:
            link.stop_recording()
        odo = dict(kv.split('=') for kv in line.split()[2:] if '=' in kv)
        x, y, yaw = float(odo['x']), float(odo['y']), float(odo['yaw'])
        print(f'\ncommanded: x {x:.1f} mm, y {y:.1f} mm, yaw {yaw:.1f} deg')

        if args.mode == 'straight':
            d = float(input('measured distance moved (mm): '))
            h = float(input('measured heading change (deg, left +): '))
            err = (d - math.hypot(x, y)) / math.hypot(x, y) * 100
            print(f'distance error {err:+.1f} %  (goal |err| <= 10 %),  heading {h - yaw:+.1f} deg  (goal <= 5)')
        else:
            a = float(input('measured turn (deg, left +): '))
            print(f'turn error {a - yaw:+.1f} deg  (goal |err| <= 10)')
    except TimeoutError as e:
        print(f'\n{e}')
    except KeyboardInterrupt:
        print()
    finally:
        done.set()
        try:
            link.event('B')
            time.sleep(0.5)
            link.close()
        except SystemExit:
            pass


if __name__ == '__main__':
    main()
