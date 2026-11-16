#pragma once

// Link lengths (mm)
const float L1 = 62.0f;
const float L2 = 76.0f;
const float L3 = 132.0f;

// Forward kinematics of one leg.
// Input:  joint angles theta1..3 (deg)
// Output: toe position in leg frame, toe[0..2] = x, y, z (mm)
void fk(float theta1, float theta2, float theta3, float toe[3]);
