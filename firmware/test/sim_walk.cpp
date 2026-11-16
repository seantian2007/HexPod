// Runs the ESP32 control pipeline (no hardware) on a scripted input and prints every frame.
// stdin:  one line per frame: lx ly rx gait_request   (gait_request = -1 for none, else 0/1/2)
// stdout: vx vy w  stopped  feet[18]  ik_ok  thetas[18]
// Used by golden_walk.py to compare against the Python code.
#include <stdio.h>
#include "../hexapod/src/core/body_ik.h"
#include "../hexapod/src/core/walker.h"
#include "../hexapod/src/core/command.h"

int main() {
    const double dt = 0.02;
    Walker walker(TRIPOD, GAIT_CFG[TRIPOD].T, 30.0f);
    CommandShaper shaper;
    int pending = -1;
    float lx, ly, rx;
    int req;
    const float pose[6] = {0, 0, 0, 0, 0, 0};

    while (scanf("%f %f %f %d", &lx, &ly, &rx, &req) == 4) {
        // same order as one frame of telop.py:
        // 1. shape the command (ramps to zero while a gait change is pending)
        float cmd[3];
        if (pending >= 0) {
            shaper.shape(0, 0, 0, dt, cmd);
        } else {
            shaper.shape(lx, ly, rx, dt, cmd);
        }
        // 2. button -> pending gait change
        if (req >= 0 && pending < 0) {
            pending = req;
        }
        // 3. switch gait once the walker has stopped
        if (pending >= 0 && walker.stopped) {
            walker.set_gait((Gait)pending, GAIT_CFG[pending].T);
            shaper.set_gait((Gait)pending);
            pending = -1;
        }
        // 4. feet and joint angles
        float feet[NUM_LEGS][3], th[NUM_LEGS][3];
        int status[NUM_LEGS];
        walker.step(cmd[0], cmd[1], cmd[2], dt, feet);
        bool ok = body_ik(pose, feet, th, status);

        printf("%.5f %.5f %.5f %d", (double)cmd[0], (double)cmd[1], (double)cmd[2], walker.stopped ? 1 : 0);
        for (int i = 0; i < NUM_LEGS; i++)
            for (int k = 0; k < 3; k++) printf(" %.5f", (double)feet[i][k]);
        printf(" %d", ok ? 1 : 0);
        for (int i = 0; i < NUM_LEGS; i++)
            for (int k = 0; k < 3; k++) printf(" %.5f", (double)(ok ? th[i][k] : 0.0f));
        printf("\n");
    }
    return 0;
}
