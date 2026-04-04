#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <inttypes.h>

#define SMALL   100
#define MEDIUM  10000
#define LARGE   1000000

static int64_t arr[LARGE];

static int64_t summation(int n) {
    int64_t sum = 0;
    for (int i = 0; i < n; i++) {
        sum += arr[i];
    }
    return sum;
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: summation <small|medium|large>\n");
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
        arr[i] = (int64_t)i + 1;
    }

    printf("%" PRId64 "\n", summation(n));
    return 0;
}
