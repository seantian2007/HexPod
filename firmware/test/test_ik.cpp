#include <stdio.h>
#include <math.h>
#include "../hexapod/src/core/fk.h"
#include "../hexapod/src/core/ik.h"

int main() {
    // 1. Round trip: fk(theta) -> ik -> compare with theta
    const float th[7][3] = {{0, 0, 0}, {0, 0, 90}, {30, 0, 90}, {0, 30, 105},
                            {-20, 30, 105}, {0, 45, 135}, {45, -20, 60}};
    for (int i = 0; i < 7; i++) {
        float toe[3], out[3] = {0, 0, 0};
        fk(th[i][0], th[i][1], th[i][2], toe);
        int s = ik(toe, out);
        float err = 0;
        for (int k = 0; k < 3; k++) err = fmaxf(err, fabsf(out[k] - th[i][k]));
        printf("round trip %d: status %d, max err %.6f deg\n", i, s, (double)err);
    }

    // 2. Unreachable points -> expect failure status
    const float bad[3][3] = {{400, 0, 0}, {80, 0, 0}, {0, 200, -90}};
    for (int i = 0; i < 3; i++) {
        float out[3];
        printf("unreachable %d: status %d\n", i, ik(bad[i], out));
    }
    return 0;
}
