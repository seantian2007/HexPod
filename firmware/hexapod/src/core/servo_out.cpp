#include "servo_out.h"

int clamp_frame(float th[NUM_JOINTS], const float prev[NUM_JOINTS], float max_step) {
    int n = 0;
    for (int i = 0; i < NUM_JOINTS; i++) {
        float lo = JOINT_MIN[i % 3], hi = JOINT_MAX[i % 3];
        if (prev[i] - max_step > lo) lo = prev[i] - max_step;
        if (prev[i] + max_step < hi) hi = prev[i] + max_step;
        if (th[i] < lo) { th[i] = lo; n++; }
        else if (th[i] > hi) { th[i] = hi; n++; }
    }
    return n;
}

void angles_to_pulses(const float th[NUM_JOINTS], float us[NUM_JOINTS]) {
    for (int i = 0; i < NUM_JOINTS; i++) {
        float s = (i >= 9) ? -1.0f : 1.0f;
        int joint = i % 3;
        if (joint == 0) {
            us[i] = ZERO_PULSE[i] + th[i] * PULSE_PER_DEGREE;
        } else if (joint == 1) {
            us[i] = ZERO_PULSE[i] + s * th[i] * PULSE_PER_DEGREE;
        } else {
            us[i] = ZERO_PULSE[i] + s * (th[i] - 90.0f) * PULSE_PER_DEGREE;
        }
    }
}
