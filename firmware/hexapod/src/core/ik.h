#pragma once
#include "fk.h"   // L1, L2, L3

// Status codes (enum)
enum ErrorState {
    IK_OK = 0,
    NON_SOLVABLE = 4,
    THETA_1_ERROR = 1,
    THETA_2_ERROR = 2,
    THETA_3_ERROR = 3

};

// Joint limits (deg)
const float COXA_RANGE_DEGREE_LOW = -45.0f;
const float COXA_RANGE_DEGREE_HIGH = 45.0f;
const float FEMUR_RANGE_DEGREE_LOW = -75.0f;
const float FEMUR_RANGE_DEGREE_HIGH = 75.0f;
const float TIBIA_RANGE_DEGREE_LOW = 15.0f;
const float TIBIA_RANGE_DEGREE_HIGH = 165.0f;

// ik() declaration: inputs (mm), outputs (deg), return value
int ik(const float poses[3], float thetas[3]);
