#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <inttypes.h>

#define SMALL   50
#define MEDIUM  200
#define LARGE   500
#define N_MAX   LARGE

static int64_t a[N_MAX][N_MAX];
static int64_t b[N_MAX][N_MAX];
static int64_t c[N_MAX][N_MAX];

static void fill_matrices(int n) {
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            a[i][j] = (int64_t)i + (int64_t)j;
            b[i][j] = (int64_t)i - (int64_t)j;
        }
    }
}

static void matrix_multiply(int n) {
    memset(c, 0, sizeof(c));
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            int64_t acc = 0;
            for (int k = 0; k < n; k++) {
                acc += a[i][k] * b[k][j];
            }
            c[i][j] = acc;
        }
    }
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: matrix_multiplication <small|medium|large>\n");
        return 1;
    }

    int n;
    if      (strcmp(argv[1], "small")  == 0) n = SMALL;
    else if (strcmp(argv[1], "medium") == 0) n = MEDIUM;
    else if (strcmp(argv[1], "large")  == 0) n = LARGE;
    else {
        fprintf(stderr, "Unknown size: %s\n", argv[1]);
        return 1;
    }

    fill_matrices(n);
    matrix_multiply(n);
    printf("%" PRId64 "\n", c[n / 2][n / 2]);
    return 0;
}
