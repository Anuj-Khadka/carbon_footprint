#include <stdio.h>
#include <stdint.h>
#include <inttypes.h>

#define N 10000

static int64_t arr[N];

static void setup(void) {
    for (int i = 0; i < N; i++) {
        arr[i] = (int64_t)i * 2;
    }
}

static int binary_search(void) {
    int64_t target = (int64_t)(N - 1) * 2;
    int lo = 0, hi = N - 1;
    while (lo <= hi) {
        int mid = lo + (hi - lo) / 2;
        if      (arr[mid] == target) return mid;
        else if (arr[mid] < target)  lo = mid + 1;
        else                         hi = mid - 1;
    }
    return -1;
}

int main(void) {
    setup();

    printf("ready\n");
    fflush(stdout);

    char buf[64];
    while (fgets(buf, sizeof(buf), stdin)) {
        printf("%d\n", binary_search());
        fflush(stdout);
    }

    return 0;
}