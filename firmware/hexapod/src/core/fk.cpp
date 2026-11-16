#include "fk.h"
#include <math.h>

static const float DEG2RAD = 3.14159265f / 180.0f;

void fk(float theta1, float theta2, float theta3, float toe[3]) {
    float t1  = theta1 * DEG2RAD;
    float t2  = theta2 * DEG2RAD;
    float t23 = (theta2 - theta3) * DEG2RAD;

    float r = L1 + L2 * cosf(t2) + L3 * cosf(t23);
    toe[0] = r * cosf(t1);
    toe[1] = r * sinf(t1);
    toe[2] = L2 * sinf(t2) + L3 * sinf(t23);
}
