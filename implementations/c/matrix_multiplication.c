#include <stdio.h>
#include <stdint.h>
#include <inttypes.h>

#define N 300

static int64_t a[N][N];
static int64_t b[N][N];
static int64_t c[N][N];

static void matrix_multiply(void) {
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            int64_t acc = 0;
            for (int k = 0; k < N; k++) {
                acc += a[i][k] * b[k][j];
            }
            c[i][j] = acc;
        }
    }
}

int main(void) {
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            a[i][j] = (int64_t)i + (int64_t)j;
            b[i][j] = (int64_t)i - (int64_t)j;
        }
    }

    matrix_multiply();

    printf("%" PRId64 "\n", c[N / 2][N / 2]);
    return 0;
}