#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <inttypes.h>

#define N 1000000

int64_t merge_once_buffer(int64_t *arr, int64_t *temp, size_t left, size_t mid, size_t right) {
    for (size_t i = left; i <= right; i++) {
        temp[i] = arr[i];
    }

    size_t i = left;
    size_t j = mid + 1;
    size_t k = left;

    while (i <= mid && j <= right) {
        arr[k++] = (temp[i] <= temp[j]) ? temp[i++] : temp[j++];
    }

    while (i <= mid) {
        arr[k++] = temp[i++];
    }

    while (j <= right) {
        arr[k++] = temp[j++];
    }
    return 0;
}

int64_t merge_sort_impl(int64_t *arr, int64_t *temp, size_t left, size_t right) {
    if (left >= right) {
        return 0;
    }

    size_t mid = left + (right - left) / 2;
    merge_sort_impl(arr, temp, left, mid);
    merge_sort_impl(arr, temp, mid + 1, right);
    merge_once_buffer(arr, temp, left, mid, right);
    return 0;
}

int64_t merge_sort(int64_t *arr, size_t n) {
    if (arr == NULL || n < 2) {
        return 0;
    }

    int64_t *temp = malloc(n * sizeof(*temp));
    if (temp == NULL) {
        return 1;
    }

    merge_sort_impl(arr, temp, 0, n - 1);
    free(temp);
    return 0;
}

int main(void) {
    int64_t *arr = malloc((size_t)N * sizeof(*arr));
    if (arr == NULL) {
        fprintf(stderr, "Memory allocation failed\n");
        return 1;
    }

    for (size_t i = 0; i < (size_t)N; i++) {
        arr[i] = (int64_t)(N - (int)i);
    }

    if (merge_sort(arr, (size_t)N) != 0) {
        fprintf(stderr, "Sort failed\n");
        free(arr);
        return 1;
    }

    printf("%" PRId64 "\n", arr[N - 1]);

    free(arr);
    return 0;
}