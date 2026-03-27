#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <inttypes.h>

#define N 10000000

int64_t summation(int64_t *arr, int n) {
    int64_t sum = 0;
    for (int i = 0; i < n; i++) {
        sum += arr[i];
    }
    return sum;
}

int main(void) {
    int64_t *arr = malloc(N * sizeof(int64_t));
    if (arr == NULL) {
        fprintf(stderr, "Memory allocation failed\n");
        return 1;
    }

    for (int i = 0; i < N; i++) {
        arr[i] = i + 1;
    }

    int64_t result = summation(arr, N);

    printf("%" PRId64 "\n", result);

    free(arr);
    return 0;
}
