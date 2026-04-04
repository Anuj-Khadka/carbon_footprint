#include <stdio.h>
#include <stdint.h>
#include <inttypes.h>

#define N 1000000

static int64_t arr[N];
static int64_t temp[N];

static void setup(void) {
    
}

static void reset(void) {
    for (int i = 0; i < N; i++) {
        arr[i] = (int64_t)(N - i);
    }
}

static void merge(int left, int mid, int right) {
    for (int i = left; i <= right; i++) {
        temp[i] = arr[i];
    }
    int i = left, j = mid + 1, k = left;
    while (i <= mid && j <= right) {
        arr[k++] = (temp[i] <= temp[j]) ? temp[i++] : temp[j++];
    }
    while (i <= mid)   arr[k++] = temp[i++];
    while (j <= right) arr[k++] = temp[j++];
}

static void merge_sort_impl(int left, int right) {
    if (left >= right) return;
    int mid = left + (right - left) / 2;
    merge_sort_impl(left, mid);
    merge_sort_impl(mid + 1, right);
    merge(left, mid, right);
}

static int64_t merge_sort(void) {
    reset();
    merge_sort_impl(0, N - 1);
    return arr[N - 1];
}

int main(void) {
    setup();

    printf("ready\n");
    fflush(stdout);

    char buf[64];
    while (fgets(buf, sizeof(buf), stdin)) {
        printf("%" PRId64 "\n", merge_sort());
        fflush(stdout);
    }

    return 0;
}