#pragma once
#include "geometry.h"

// R = Rz(yaw) Ry(pitch) Rx(roll), angles in deg (= utils/Rotation.rot)
void rot(float roll, float pitch, float yaw, float R[3][3]);

// Body IK (= utils/body_ik.body_ik).
// pose:   body x, y, z (mm), roll, pitch, yaw (deg)
// feet:   6 feet positions in world frame (mm)
// thetas: 6 x (coxa, femur, tibia) in deg, written only for legs that succeed
// status: per-leg ik() result (IK_OK or an error code)
// Returns true if all six legs succeed.
bool body_ik(const float pose[6], const float feet[NUM_LEGS][3],
             float thetas[NUM_LEGS][3], int status[NUM_LEGS]);
