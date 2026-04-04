#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <inttypes.h>

#define N 50

static int64_t a[N][N];
static int64_t b[N][N];
static int64_t c[N][N];

static void setup(void) {
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            a[i][j] = (int64_t)i + (int64_t)j;
            b[i][j] = (int64_t)i - (int64_t)j;
        }
    }
}

static int64_t matrix_mul(void) {
    memset(c, 0, sizeof(c));
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            int64_t acc = 0;
            for (int k = 0; k < N; k++) {
                acc += a[i][k] * b[k][j];
            }
            c[i][j] = acc;
        }
    }
    return c[N / 2][N / 2];
}

int main(void) {
    setup();

    printf("ready\n");
    fflush(stdout);

    char buf[64];
    while (fgets(buf, sizeof(buf), stdin)) {
        printf("%" PRId64 "\n", matrix_mul());
        fflush(stdout);
    }

    return 0;
}