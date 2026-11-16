#include "ik.h"
#include <math.h>

// File-local constants (DEG2RAD, RAD2DEG, tolerance)
static const float DEG2RAD = 3.14159265f / 180.0f;
static const float RAD2DEG = 180.0f / 3.14159265f;
static const float tol = 1.0e-4f;


// ik() definition
int ik(const float poses[3], float thetas[3]) {
    float x = poses[0];
    float y = poses[1];
    float z = poses[2];

    float theta1 = atan2f(y, x) * RAD2DEG;
    float r = sqrtf(x * x + y * y);

    if (theta1 < -90.0f) {
        theta1 += 180.0f;
        r *= -1.0f;
    } else if (theta1 > 90.0f) {
        theta1 -= 180.0f;
        r *= -1.0f;
    }

    if (!(theta1 <= COXA_RANGE_DEGREE_HIGH + tol && theta1 >= COXA_RANGE_DEGREE_LOW - tol)) {
        return THETA_1_ERROR;
    }

    float u = r - L1;
    float D = sqrtf(u * u + z * z);

    if (D > L2 + L3 || D < L3 - L2) {
        return NON_SOLVABLE;
    }

    float theta3 = acosf((D * D - L2 * L2 - L3 * L3)/(2.0f * L2 * L3)) * RAD2DEG;

    if (!(theta3 >= TIBIA_RANGE_DEGREE_LOW - tol && theta3 <= TIBIA_RANGE_DEGREE_HIGH + tol)) {
        return THETA_3_ERROR;
    }

    float alpha = atan2f(z, u);
    float beta = atan2f(L3 * sinf(theta3 * DEG2RAD), L2 + L3 * cosf(theta3 * DEG2RAD));
    float theta2 = (alpha + beta) * RAD2DEG;

    if (theta2 > 180.0f) {
        theta2 -= 360.0f;
    } else if (theta2 < -180.0f) {
        theta2 += 360.0f;
    }

    if (!(theta2 >= FEMUR_RANGE_DEGREE_LOW - tol && theta2 <= FEMUR_RANGE_DEGREE_HIGH + tol)) {
        return THETA_2_ERROR;
    }

    thetas[0] = theta1;
    thetas[1] = theta2;
    thetas[2] = theta3;

    return IK_OK;
}
