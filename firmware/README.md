# firmware

- `hexapod/` – ESP32 sketch (Arduino IDE, board: ESP32 Dev Module, esp32 core 3.x, library Adafruit PWM Servo Driver). Arduino only compiles the sketch folder and `src/`, so shared code lives in `hexapod/src/core/`.
- `hexapod/src/core/` – plain C++ (no Arduino.h), used by both the sketch and the Mac tests. Each file mirrors a Python module:

  | C++ | Python |
  |---|---|
  | fk, ik | utils/fk.py, utils/ik.py |
  | geometry.h | constants.py |
  | body_ik | utils/Rotation.py, utils/body_ik.py |
  | gait | utils/gaits.py |
  | walker | utils/walker.py |
  | command | GamePad.read() + apply_gait_limits() in telop.py |
  | servo_out | utils/AngleToPulse.py + output clamp |

- `test/` – Mac-only tests against the Python code.
- `../esp_teleop.py` – gamepad on the computer, sends sticks/buttons to the ESP32.

## WiFi (stage 8, branch dev-code_wifi)

The ESP32 is a WiFi access point. After uploading, the serial monitor (115200) prints the
network name `hexapod-XXXX` and the password (`WIFI_PASSWORD` in hexapod.ino). Join it from
the Mac; the robot is `192.168.4.1`, UDP port 1234. USB serial still works as before.

From `code/`:

```
python3 link_test.py                       # W2: loss < 1 %, p99 round trip < 50 ms
python3 esp_teleop.py                      # WiFi (X = start / stop recording to logs/)
python3 esp_teleop.py --serial             # USB, as in stage 7
python3 walk_test.py straight --record     # floor test + per-frame CSV in logs/
```

`utils/esp_link.py` hides the difference: `open_link(args)` gives a UDP or a serial link
with the same `send()`, `event()`, `wait_for()`, `start_recording()`.

Tests (from `firmware/test/`):

```
clang++ -std=c++17 -Wall -Wdouble-promotion -O2 test_fk.cpp ../hexapod/src/core/fk.cpp -o test_fk && ./test_fk
clang++ -std=c++17 -Wall -Wdouble-promotion -O2 test_ik.cpp ../hexapod/src/core/fk.cpp ../hexapod/src/core/ik.cpp -o test_ik && ./test_ik
clang++ -std=c++17 -Wall -Wdouble-promotion -O2 sim_walk.cpp ../hexapod/src/core/*.cpp -o sim_walk && python3 golden_walk.py
```
