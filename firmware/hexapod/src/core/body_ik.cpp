#include "body_ik.h"
#include <math.h>

static const float DEG2RAD = 3.14159265f / 180.0f;

void rot(float roll, float pitch, float yaw, float R[3][3]) {
    float cr = cosf(roll * DEG2RAD),  sr = sinf(roll * DEG2RAD);
    float cp = cosf(pitch * DEG2RAD), sp = sinf(pitch * DEG2RAD);
    float cy = cosf(yaw * DEG2RAD),   sy = sinf(yaw * DEG2RAD);

    // Rz @ Ry @ Rx written out
    R[0][0] = cy * cp;  R[0][1] = cy * sp * sr - sy * cr;  R[0][2] = cy * sp * cr + sy * sr;
    R[1][0] = sy * cp;  R[1][1] = sy * sp * sr + cy * cr;  R[1][2] = sy * sp * cr - cy * sr;
    R[2][0] = -sp;      R[2][1] = cp * sr;                 R[2][2] = cp * cr;
}

bool body_ik(const float pose[6], const float feet[NUM_LEGS][3],
             float thetas[NUM_LEGS][3], int status[NUM_LEGS]) {
    float R[3][3];
    rot(pose[3], pose[4], pose[5], R);
    bool all_ok = true;

    for (int i = 0; i < NUM_LEGS; i++) {
        // foot relative to body origin, in world axes
        float d[3] = {feet[i][0] - pose[0], feet[i][1] - pose[1], feet[i][2] - pose[2]};

        // R^T d - mount   (foot in body frame, relative to the coxa mount)
        float q[3];
        for (int r = 0; r < 3; r++) {
            q[r] = R[0][r] * d[0] + R[1][r] * d[1] + R[2][r] * d[2];
        }
        q[0] -= LEG_MOUNT[i][0];
        q[1] -= LEG_MOUNT[i][1];

        // Rz(-alpha) q   (into the leg frame)
        float c = cosf(LEG_ALPHA[i] * DEG2RAD), s = sinf(LEG_ALPHA[i] * DEG2RAD);
        float p[3] = {c * q[0] + s * q[1], -s * q[0] + c * q[1], q[2]};

        status[i] = ik(p, thetas[i]);
        if (status[i] != IK_OK) {
            all_ok = false;
        }
    }
    return all_ok;
}
