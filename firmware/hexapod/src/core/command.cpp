#include "command.h"
#include <math.h>

const GaitConfig GAIT_CFG[NUM_GAITS] = {
    {2.5f, 0.38f,  0.15f},    // tripod
    {3.0f, 0.16f,  0.075f},   // ripple
    {6.0f, 0.075f, 0.035f},   // wave
};

CommandShaper::CommandShaper() {
    reset();
    set_gait(TRIPOD);
}

void CommandShaper::set_gait(Gait g) {
    v_max = GAIT_CFG[g].v * JOINT_SPEED_LIMIT;
    w_max = fminf(GAIT_CFG[g].w * JOINT_SPEED_LIMIT, W_CAP);
    // keep the AEP drift speed ~31 mm/s when the command changes mid-swing
    accel = (float)(31.0 / (GAITS[g].beta * (double)GAIT_CFG[g].T / 2.0));
}

void CommandShaper::reset() {
    last[0] = last[1] = last[2] = 0.0f;
}

static float clampf(float x, float lo, float hi) {
    return x < lo ? lo : (x > hi ? hi : x);
}

void CommandShaper::shape(float lx, float ly, float rx, float dt, float cmd[3]) {
    float c[3] = {ly * v_max, -lx * v_max, -rx * w_max};

    // combined limit: translation and turning share the joint speed budget
    float lim = hypotf(c[0], c[1]) / v_max + fabsf(c[2]) / w_max;
    if (lim > 1.0f) {
        for (int k = 0; k < 3; k++) c[k] /= lim;
    }

    // acceleration limit
    float step[3] = {accel * dt, accel * dt, accel * dt * w_max / v_max};
    for (int k = 0; k < 3; k++) {
        cmd[k] = last[k] + clampf(c[k] - last[k], -step[k], step[k]);
        last[k] = cmd[k];
    }
}
