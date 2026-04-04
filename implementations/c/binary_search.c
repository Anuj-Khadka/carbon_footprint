#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <inttypes.h>

#define SMALL   100
#define MEDIUM  10000
#define LARGE   1000000

static int64_t arr[LARGE];

static int binary_search(int n, int64_t target) {
    int lo = 0, hi = n - 1;
    while (lo <= hi) {
        int mid = lo + (hi - lo) / 2;
        if (arr[mid] == target)      return mid;
        else if (arr[mid] < target)  lo = mid + 1;
        else                         hi = mid - 1;
    }
    return -1;
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: binary_search <small|medium|large>\n");
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

    for (int i = 0; i < n; i++) {
        arr[i] = (int64_t)i * 2;
    }

    int64_t target = (int64_t)(n - 1) * 2;
    printf("%d\n", binary_search(n, target));
    return 0;
}
