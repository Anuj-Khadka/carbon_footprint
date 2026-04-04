#include <stdio.h>
#include <stdint.h>
#include <inttypes.h>

#define N 10000

static int64_t arr[N];

static void setup(void) {
    for (int i = 0; i < N; i++) {
        arr[i] = (int64_t)i + 1;
    }
}

static int64_t summation(void) {
    int64_t sum = 0;
    for (int i = 0; i < N; i++) {
        sum += arr[i];
    }
    return sum;
}

int main(void) {
    setup();

    printf("ready\n");
    fflush(stdout);

    char buf[64];
    while (fgets(buf, sizeof(buf), stdin)) {
        printf("%" PRId64 "\n", summation());
        fflush(stdout);
    }

    return 0;
}