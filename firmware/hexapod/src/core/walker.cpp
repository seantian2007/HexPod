#include "walker.h"
#include <math.h>

static const float EPS_V = 0.5f;     // mm/s, below this the command counts as zero
static const float EPS_W = 0.2f;     // deg/s
static const float PI_F = 3.14159265f;

Walker::Walker(Gait gait_, double T_, float h_, double idle_time_)
    : stopped(true), gait(gait_), T(T_), t(0.0), idle_time(idle_time_), idle(0.0), h(h_) {
    beta = GAITS[gait].beta;
    for (int i = 0; i < NUM_LEGS; i++) {
        for (int k = 0; k < 3; k++) {
            p0[i][k] = F_DEFAULT[i][k];
            p[i][k] = F_DEFAULT[i][k];
            lift[i][k] = 0.0f;
        }
        was_stance[i] = true;
        settled[i] = false;
        hold[i] = false;
    }
    start_hold();
}

bool Walker::set_gait(Gait g, double T_) {
    if (!stopped) {
        return false;
    }
    gait = g;
    T = T_;
    beta = GAITS[g].beta;
    t = (GAITS[g].delta[0] + beta) * T;    // start when R1 begins its swing
    start_hold();
    return true;
}

// Shift t so the first swinging leg starts at s = 0; hold other mid-swing legs.
void Walker::start_hold() {
    bool st;
    double s;
    double min_swing = 2.0;
    for (int i = 0; i < NUM_LEGS; i++) {
        leg_phase(i, t, T, gait, &st, &s);
        if (!st && s < min_swing) {
            min_swing = s;
        }
    }
    if (min_swing <= 1.0) {
        t -= min_swing * (1.0 - beta) * T;
    }
    double one_frame = 0.02 / ((1.0 - beta) * T);
    for (int i = 0; i < NUM_LEGS; i++) {
        leg_phase(i, t, T, gait, &st, &s);
        hold[i] = (!st) && s > one_frame;
    }
}

void Walker::step(float vx, float vy, float w, double dt, float feet[NUM_LEGS][3]) {
    // auto stop / start
    bool moving = fabsf(vx) > EPS_V || fabsf(vy) > EPS_V || fabsf(w) > EPS_W;
    if (moving) {
        idle = 0.0;
        if (stopped) {
            stopped = false;
            start_hold();
        } else {
            // restarted while settling: hold settled legs that are mid-swing
            for (int i = 0; i < NUM_LEGS; i++) {
                if (settled[i]) {
                    bool st;
                    double s;
                    leg_phase(i, t, T, gait, &st, &s);
                    hold[i] = hold[i] || !st;
                }
            }
        }
        for (int i = 0; i < NUM_LEGS; i++) {
            settled[i] = false;
        }
    } else {
        idle += dt;
    }

    if (!stopped) {
        bool settling = idle >= idle_time;
        float w_rad = w * PI_F / 180.0f;
        float k = (float)(beta * T / 2.0);
        float fdt = (float)dt;

        for (int i = 0; i < NUM_LEGS; i++) {
            bool in_stance;
            double s_d;
            leg_phase(i, t, T, gait, &in_stance, &s_d);
            float s = (float)s_d;
            if (hold[i]) {                          // held legs stay in stance until their phase does
                if (in_stance) {
                    hold[i] = false;
                } else {
                    in_stance = true;
                }
            }
            if (settling && settled[i]) {           // settled legs don't lift again
                in_stance = true;
            }

            if (in_stance) {
                if (settling && !was_stance[i]) {   // swing leg just landed at p0
                    settled[i] = true;
                }
                float xc = p[i][0], yc = p[i][1];
                p[i][0] = xc - (vx - w_rad * yc) * fdt;
                p[i][1] = yc - (vy + w_rad * xc) * fdt;
                p[i][2] = p0[i][2];
            } else {
                if (was_stance[i]) {
                    for (int a = 0; a < 3; a++) lift[i][a] = p[i][a];
                }
                float aep_x = p0[i][0] + k * (vx - w_rad * p0[i][1]);
                float aep_y = p0[i][1] + k * (vy + w_rad * p0[i][0]);
                float c = s - sinf(2.0f * PI_F * s) / (2.0f * PI_F);
                p[i][0] = lift[i][0] + c * (aep_x - lift[i][0]);
                p[i][1] = lift[i][1] + c * (aep_y - lift[i][1]);
                p[i][2] = p0[i][2] + h * (1.0f - cosf(2.0f * PI_F * s)) / 2.0f;
            }
            was_stance[i] = in_stance;
        }

        t += dt;

        // all legs settled at p0 -> stop
        bool all_settled = true;
        for (int i = 0; i < NUM_LEGS; i++) {
            all_settled = all_settled && settled[i];
        }
        if (settling && all_settled) {
            stopped = true;
            for (int i = 0; i < NUM_LEGS; i++) {
                p[i][2] = p0[i][2];
                was_stance[i] = true;
            }
        }
    }

    for (int i = 0; i < NUM_LEGS; i++) {
        for (int a = 0; a < 3; a++) feet[i][a] = p[i][a];
    }
}
