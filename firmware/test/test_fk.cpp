#include <stdio.h>
#include "../hexapod/src/core/fk.h"

int main() {
    const float th1[7] = {0, 0, 30, 0, -20, 0, 45};
    const float th2[7] = {0, 0, 0, 30, 30, 45, -20};
    const float th3[7] = {0, 90, 90, 105, 105, 135, 60};

    for (int i = 0; i < 7; i++) {
        float toe[3];
        fk(th1[i], th2[i], th3[i], toe);
        printf("%d: %8.3f %8.3f %8.3f\n", i,
               (double)toe[0], (double)toe[1], (double)toe[2]);
    }
    return 0;
}
