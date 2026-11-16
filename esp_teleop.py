"""Gamepad -> ESP32 (stage 7/8 firmware). The ESP32 does the walking; this script only
sends the sticks and button presses, and prints what the ESP32 reports.

Run from code/:
    python3 esp_teleop.py                 # over WiFi: first join the hexapod-xxxx network
    python3 esp_teleop.py --serial        # over USB (default port /dev/cu.usbserial-0001)
    python3 esp_teleop.py --serial /dev/cu.usbserial-0002

  left stick   walk / strafe        right stick x   turn
  A            stand up / reset     B               stop, park and quit
  D-pad L/R    previous / next gait (switches once all feet are down)
  X            start / stop recording -> logs/<date>_<time>.csv (WiFi only)
"""
import argparse
import time

from utils.esp_link import add_link_args, open_link
from utils.gamepad import GamePad

RATE = 20          # Hz; the ESP32 stops walking if nothing arrives for 300 ms


def main():
    ap = argparse.ArgumentParser()
    add_link_args(ap)
    args = ap.parse_args()

    link = open_link(args)
    joy = GamePad()
    print(__doc__)
    link.send('S')                     # the robot answers with its state, so we see it is there
    seq = 0
    t0 = time.perf_counter()
    try:
        while True:
            seq += 1
            while time.perf_counter() < t0 + seq / RATE:
                time.sleep(0.002)
            joy._poll()
            lx, ly, rx, _ = joy.sticks()
            link.send(f'C,{seq},{lx:.3f},{ly:.3f},{rx:.3f}')
            if joy.pressed('reset'):
                link.event('A')
            if joy.pressed('gait_next'):
                link.event('N')
            if joy.pressed('gait_prev'):
                link.event('P')
            if joy.pressed('dance'):   # button X
                if link.recording:
                    link.stop_recording()
                    print('recording stopped')
                else:
                    path = link.start_recording()
                    if path:
                        print(f'recording -> {path}')
            if joy.pressed('quit'):
                break
    except KeyboardInterrupt:
        pass
    finally:
        try:
            link.event('B')            # park: the robot settles and stands
            time.sleep(0.5)
            link.close()
        except SystemExit:
            pass                       # already disconnected; the message is printed on exit
        print('closed')


if __name__ == '__main__':
    main()
