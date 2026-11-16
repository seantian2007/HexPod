#pragma once
// Gait tables and leg phase (= utils/gaits.py).

enum Gait { TRIPOD = 0, RIPPLE = 1, WAVE = 2 };
const int NUM_GAITS = 3;

struct GaitDef {
    const char* name;
    double beta;       // duty factor: fraction of the cycle in stance
    double delta[6];   // phase offset per leg (R1..L3)
};

extern const GaitDef GAITS[NUM_GAITS];

// Phase of one leg at time t (s) with period T (s).
// in_stance: true = foot on the ground; s: progress 0..1 within stance or swing.
// Time and phase use double on purpose: see walker.h.
void leg_phase(int leg, double t, double T, Gait gait, bool* in_stance, double* s);
