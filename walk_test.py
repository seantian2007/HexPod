"""Open-loop accuracy test (stage 6 milestones 4 and 5) on the stage 7 firmware.

Run from code/:
    python3 walk_test.py straight            # walk forward 300 mm
    python3 walk_test.py turn                # turn left 90 deg in place
    python3 walk_test.py straight --dist 500 / turn --angle -90
    python3 walk_test.py straight --speed 0.5 --gait ripple

The script stands the robot up, waits for you to line it up, sends a full stick for
target / v_max seconds, waits until the walker has stopped, and prints the odometry the
ESP32 actually commanded. Then you type in what you measured and it prints the error.
"""
import argparse
import math
import queue
import threading
import time

import serial

RATE = 20
# v and w factors per gait (must match GAIT_CFG in command.cpp); x JOINT_SPEED_LIMIT 150
GAITS = {'tripod': (0.38, 0.15), 'ripple': (0.16, 0.075), 'wave': (0.075, 0.035)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('mode', choices=['straight', 'turn'])
    ap.add_argument('--dist', type=float, default=300, help='mm, straight mode')
    ap.add_argument('--angle', type=float, default=90, help='deg, CCW +, turn mode')
    ap.add_argument('--speed', type=float, default=1.0, help='stick fraction 0..1')
    ap.add_argument('--gait', choices=list(GAITS), default='tripod')
    ap.add_argument('--port', default='/dev/cu.usbserial-0001')
    args = ap.parse_args()
    fv, fw = GAITS[args.gait]
    v_max, w_max = fv * 150, min(fw * 150, 21)

    ser = serial.Serial()
    ser.port, ser.baudrate, ser.timeout = args.port, 115200, 0.2
    ser.dtr = ser.rts = False
    ser.open()
    lines = queue.Queue()

    def reader():
        while True:
            try:
                line = ser.readline().decode(errors='replace').strip()
            except serial.SerialException:
                return
            if line:
                print(f'[esp32] {line}')
                lines.put(line)
    threading.Thread(target=reader, daemon=True).start()

    def send(line):
        ser.write((line + '\n').encode())

    def wait_for(prefix, timeout):
        end = time.time() + timeout
        while time.time() < end:
            try:
                line = lines.get(timeout=0.1)
            except queue.Empty:
                continue
            if line.startswith(prefix):
                return line
        raise SystemExit(f'gave up waiting for "{prefix}"')

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
            send(f'C,{drive.seq},{lx:.3f},{ly:.3f},{rx:.3f}')
    drive.seq = 0

    try:
        wait_for('READY', 5)                         # opening the port resets the ESP32
        send('E,A')
        wait_for('state RUN', 5)
        for _ in range(list(GAITS).index(args.gait)):     # E,N steps tripod -> ripple -> wave
            send('E,N')
            wait_for('gait ', 5)
        input('\nPut the robot on the floor, line the plumb line up with the start mark, then press Enter ')

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
        line = wait_for('stopped: odo', 10)
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
    except KeyboardInterrupt:
        print()
    finally:
        done.set()
        try:
            send('E,B')
            time.sleep(0.5)
        except serial.SerialException:
            pass
        ser.close()


if __name__ == '__main__':
    main()
