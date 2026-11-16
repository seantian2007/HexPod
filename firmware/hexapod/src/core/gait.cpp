#include "gait.h"
#include <math.h>

const GaitDef GAITS[NUM_GAITS] = {
    {"tripod", 0.5,       {0.0, 0.5, 0.0, 0.5, 0.0, 0.5}},
    {"ripple", 2.0 / 3.0, {1.0 / 6, 5.0 / 6, 0.5, 2.0 / 3, 1.0 / 3, 0.0}},
    {"wave",   5.0 / 6.0, {1.0 / 3, 1.0 / 6, 0.0, 5.0 / 6, 2.0 / 3, 0.5}},
};

void leg_phase(int leg, double t, double T, Gait gait, bool* in_stance, double* s) {
    double beta = GAITS[gait].beta;

    // Python's % always returns 0..1; fmod keeps the sign, so fix negatives
    double phi = fmod(t / T - GAITS[gait].delta[leg], 1.0);
    if (phi < 0.0) {
        phi += 1.0;
    }

    *in_stance = phi < beta;
    *s = *in_stance ? phi / beta : (phi - beta) / (1.0 - beta);
}
