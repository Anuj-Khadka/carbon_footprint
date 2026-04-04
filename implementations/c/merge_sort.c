#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <inttypes.h>

#define SMALL   100
#define MEDIUM  10000
#define LARGE   1000000

static int64_t arr[LARGE];
static int64_t temp[LARGE];

static void merge(size_t left, size_t mid, size_t right) {
    for (size_t i = left; i <= right; i++) {
        temp[i] = arr[i];
    }
    size_t i = left, j = mid + 1, k = left;
    while (i <= mid && j <= right) {
        arr[k++] = (temp[i] <= temp[j]) ? temp[i++] : temp[j++];
    }
    while (i <= mid)   arr[k++] = temp[i++];
    while (j <= right) arr[k++] = temp[j++];
}

static void merge_sort_impl(size_t left, size_t right) {
    if (left >= right) return;
    size_t mid = left + (right - left) / 2;
    merge_sort_impl(left, mid);
    merge_sort_impl(mid + 1, right);
    merge(left, mid, right);
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: merge_sort <small|medium|large>\n");
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
        arr[i] = (int64_t)(n - i);
    }

    if (n > 1) {
        merge_sort_impl(0, (size_t)(n - 1));
    }

    printf("%" PRId64 "\n", arr[n - 1]);
    return 0;
}
