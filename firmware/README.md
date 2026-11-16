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

Tests (from `firmware/test/`):

```
clang++ -std=c++17 -Wall -Wdouble-promotion -O2 test_fk.cpp ../hexapod/src/core/fk.cpp -o test_fk && ./test_fk
clang++ -std=c++17 -Wall -Wdouble-promotion -O2 test_ik.cpp ../hexapod/src/core/fk.cpp ../hexapod/src/core/ik.cpp -o test_ik && ./test_ik
clang++ -std=c++17 -Wall -Wdouble-promotion -O2 sim_walk.cpp ../hexapod/src/core/*.cpp -o sim_walk && python3 golden_walk.py
```
