#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <inttypes.h>

#define N    1000000

static int binary_search(int64_t *arr, int n, int64_t target) {
    int lo = 0, hi = n - 1;
    while (lo <= hi) {
        int mid = lo + (hi - lo) / 2;
        if (arr[mid] == target) {
            return mid;
        }
        else if (arr[mid] <  target) {
            lo = mid + 1;
        }
        else {
            hi = mid - 1;
        }
    }
    return -1;
}

int main(void) {
    int64_t *arr = malloc(N * sizeof(int64_t));
    for (int i = 0; i < N; i++) {
        arr[i] = (int64_t)i * 2;
    }
    
    int64_t target = (int64_t)(N - 1) * 2;
    int64_t result = binary_search(arr, N, target);

    printf("%" PRId64 "\n", result);
    free(arr);
    return 0;
}
