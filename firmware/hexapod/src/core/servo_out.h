#pragma once
// Joint angles -> servo pulses (= utils/AngleToPulse.py), plus the output clamp (safety layer 3).

#include "geometry.h"

// Clamp each joint into its range and to at most max_step (deg) away from prev.
// Returns how many joints had to be clamped.
int clamp_frame(float th[NUM_JOINTS], const float prev[NUM_JOINTS], float max_step);

// th: 18 angles (deg), order R1..L3 x (coxa, femur, tibia). Writes 18 pulses (us).
// Left legs mirror femur and tibia (s = -1); tibia is measured from 90 deg.
void angles_to_pulses(const float th[NUM_JOINTS], float us[NUM_JOINTS]);
