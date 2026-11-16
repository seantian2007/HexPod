#pragma once
// Stick -> walking command, with per-gait speed limits and an acceleration limit
// (= _Pad.read() in utils/gamepad.py + apply_gait_limits() in telop.py, height fixed at 0).

#include "gait.h"

const float JOINT_SPEED_LIMIT = 150.0f;   // deg/s, = LIMIT in telop.py
const float W_CAP = 21.0f;                // deg/s, coxa range caps turning speed

struct GaitConfig {
    float T;       // period (s)
    float v;       // v_max = v * JOINT_SPEED_LIMIT (mm/s)
    float w;       // w_max = w * JOINT_SPEED_LIMIT (deg/s), capped at W_CAP
};
extern const GaitConfig GAIT_CFG[NUM_GAITS];

class CommandShaper {
public:
    CommandShaper();
    void set_gait(Gait g);

    // lx, ly, rx: sticks after deadzone, -1..1, right / up positive.
    // Writes cmd = (vx mm/s, vy mm/s, w deg/s).
    void shape(float lx, float ly, float rx, float dt, float cmd[3]);
    void reset();                   // jump to zero (used after HOLD / stand-up)

    float v_max, w_max, accel;

private:
    float last[3];
};
