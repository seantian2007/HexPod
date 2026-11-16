#pragma once
// Robot constants, copied from code/constants.py.
// Leg order everywhere: R1, R2, R3, L1, L2, L3; joints: coxa, femur, tibia.

#include "ik.h"   // joint limits, L1-L3

const int NUM_LEGS = 6;
const int NUM_JOINTS = 18;

// Coxa mount position in body frame (mm) and leg direction (deg)
const float LEG_MOUNT[NUM_LEGS][2] = {
    { 85.2f, -49.2f}, {0.0f, -98.4f}, {-85.2f, -49.2f},
    { 85.2f,  49.2f}, {0.0f,  98.4f}, {-85.2f,  49.2f},
};
const float LEG_ALPHA[NUM_LEGS] = {-30.0f, -90.0f, -150.0f, 30.0f, 90.0f, 150.0f};

// Standing pose: theta = (0, 30, 105) on every leg
const float STAND_FEMUR = 30.0f;
const float STAND_TIBIA = 105.0f;

// Default feet position in body frame (mm), = constants.F_DEFAULT
const float F_DEFAULT[NUM_LEGS][3] = {
    { 225.480566f, -130.191022f, -89.5022091f},
    {   0.0f,      -260.382045f, -89.5022091f},
    {-225.480566f, -130.191022f, -89.5022091f},
    { 225.480566f,  130.191022f, -89.5022091f},
    {   0.0f,       260.382045f, -89.5022091f},
    {-225.480566f,  130.191022f, -89.5022091f},
};

// Servo calibration: pulse (us) at theta = (0, 0, 90), = constants.ZERO_PULSE
const float ZERO_PULSE[NUM_JOINTS] = {
    1480, 1580, 1550, 1520, 1490, 1520, 1410, 1480, 1530,
    1450, 1580, 1510, 1490, 1470, 1470, 1540, 1500, 1500,
};
const float PULSE_PER_DEGREE = 2000.0f / 180.0f;

// Joint limits by joint index 0..2 (deg)
const float JOINT_MIN[3] = {COXA_RANGE_DEGREE_LOW, FEMUR_RANGE_DEGREE_LOW, TIBIA_RANGE_DEGREE_LOW};
const float JOINT_MAX[3] = {COXA_RANGE_DEGREE_HIGH, FEMUR_RANGE_DEGREE_HIGH, TIBIA_RANGE_DEGREE_HIGH};
