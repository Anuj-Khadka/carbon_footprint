#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <inttypes.h>

#define N 300

static int64_t matrix_multiply(const int64_t *a, const int64_t *b, int64_t *c, size_t n) {
    for (size_t i = 0; i < n; i++) {
        for (size_t j = 0; j < n; j++) {
            int64_t acc = 0;
            for (size_t k = 0; k < n; k++) {
                acc += a[i * n + k] * b[k * n + j];
            }
            c[i * n + j] = acc;
        }
    }
    return 0;
}

int main(void) {
    int64_t *a = malloc((size_t)N * N * sizeof(*a));
    int64_t *b = malloc((size_t)N * N * sizeof(*b));
    int64_t *c = malloc((size_t)N * N * sizeof(*c));

    if (a == NULL || b == NULL || c == NULL) {
        fprintf(stderr, "Memory allocation failed\n");
        free(a);
        free(b);
        free(c);
        return 1;
    }

    for (size_t i = 0; i < (size_t)N; i++) {
        for (size_t j = 0; j < (size_t)N; j++) {
            a[i * N + j] = (int64_t)i + (int64_t)j;
            b[i * N + j] = (int64_t)i - (int64_t)j;
        }
    }

    if (matrix_multiply(a, b, c, (size_t)N) != 0) {
        fprintf(stderr, "Matrix multiplication failed\n");
        free(a);
        free(b);
        free(c);
        return 1;
    }

    printf("%" PRId64 "\n", c[(N / 2) * N + (N / 2)]);

    free(a);
    free(b);
    free(c);
    return 0;
}
