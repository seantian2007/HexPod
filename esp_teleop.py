"""Gamepad -> ESP32 (stage 7 firmware). The ESP32 does the walking; this script only
sends the sticks and button presses, and prints what the ESP32 reports.

Run from code/:  python3 esp_teleop.py [--port /dev/cu.usbserial-0001]

  left stick   walk / strafe        right stick x   turn
  A            stand up / reset     B               stop, park and quit
  D-pad L/R    previous / next gait (switches once all feet are down)
"""
import argparse
import threading
import time

import serial

from utils.gamepad import GamePad

RATE = 20          # Hz; the ESP32 stops walking if nothing arrives for 300 ms


def reader(ser, stop):
    """Print every line the ESP32 sends (log messages and the 10 s statistics)."""
    while not stop.is_set():
        try:
            line = ser.readline().decode(errors='replace').strip()
        except serial.SerialException:
            break
        if line:
            print(f'[esp32] {line}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--port', default='/dev/cu.usbserial-0001')
    args = ap.parse_args()

    ser = serial.Serial()
    ser.port, ser.baudrate, ser.timeout = args.port, 115200, 0.2
    ser.dtr = ser.rts = False          # opening the port must not reset the ESP32
    ser.open()
    stop = threading.Event()
    threading.Thread(target=reader, args=(ser, stop), daemon=True).start()

    def send(line):
        try:
            ser.write((line + '\n').encode())
        except serial.SerialException:
            raise SystemExit('USB disconnected: the robot stops by itself after 300 ms')

    joy = GamePad()
    print(__doc__)
    seq = 0
    t0 = time.perf_counter()
    try:
        while True:
            seq += 1
            while time.perf_counter() < t0 + seq / RATE:
                time.sleep(0.002)
            joy._poll()
            lx, ly, rx, _ = joy.sticks()
            send(f'C,{seq},{lx:.3f},{ly:.3f},{rx:.3f}')
            if joy.pressed('reset'):
                send('E,A')
            if joy.pressed('gait_next'):
                send('E,N')
            if joy.pressed('gait_prev'):
                send('E,P')
            if joy.pressed('quit'):
                break
    except KeyboardInterrupt:
        pass
    finally:
        try:
            send('E,B')                # park: the robot settles and stands
            time.sleep(0.5)
        except SystemExit:
            pass                       # already disconnected; the message is printed on exit
        stop.set()
        ser.close()
        print('closed')


if __name__ == '__main__':
    main()
