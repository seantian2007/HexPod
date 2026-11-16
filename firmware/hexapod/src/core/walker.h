#pragma once
// State-based walker (= utils/walker.py, line by line).
// Feet are in the body frame; feed them to body_ik with pose = 0.
//
// Time (t, T, dt, idle) and phase are double on purpose. Adding 0.02 every frame in
// float drifts (about 3 s after an hour), and idle >= 0.3 after 15 frames is true in
// double but false in float, so the walker would stop one frame later than Python.
// These are a few operations per frame, so the slow double math costs microseconds.
// Positions stay float.

#include "geometry.h"
#include "gait.h"

class Walker {
public:
    Walker(Gait gait = TRIPOD, double T = 2.5, float h = 30.0f, double idle_time = 0.3);

    // Switch gait; only allowed while stopped. Returns false otherwise.
    bool set_gait(Gait gait, double T);

    // vx, vy: body speed (mm/s, x forward, y left); w: turn rate (deg/s, CCW +).
    // Writes the new feet positions into feet.
    void step(float vx, float vy, float w, double dt, float feet[NUM_LEGS][3]);

    // Gait cycle progress 0..1 (read-only, for the data log). Does not change the walk.
    double phase() const;

    bool stopped;                   // all feet down at p0, phase frozen
    bool was_stance[NUM_LEGS];      // stance flag of the last step
    Gait gait;
    double T;

private:
    void start_hold();

    double t, beta, idle_time, idle;
    float h;
    float p0[NUM_LEGS][3], p[NUM_LEGS][3], lift[NUM_LEGS][3];
    bool settled[NUM_LEGS];         // legs that landed at p0 while settling
    bool hold[NUM_LEGS];            // legs mid-swing at start-up, kept in stance
};
