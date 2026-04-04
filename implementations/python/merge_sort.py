import sys

SMALL  = 100
MEDIUM = 10000
LARGE  = 1000000

SIZES = {"small": SMALL, "medium": MEDIUM, "large": LARGE}

def merge(arr, temp, left, mid, right):
    for i in range(left, right + 1):
        temp[i] = arr[i]
    i, j, k = left, mid + 1, left
    while i <= mid and j <= right:
        if temp[i] <= temp[j]:
            arr[k] = temp[i]
            i += 1
        else:
            arr[k] = temp[j]
            j += 1
        k += 1
    while i <= mid:
        arr[k] = temp[i]
        i += 1
        k += 1
    while j <= right:
        arr[k] = temp[j]
        j += 1
        k += 1

def merge_sort_impl(arr, temp, left, right):
    if left >= right:
        return
    mid = left + (right - left) // 2
    merge_sort_impl(arr, temp, left, mid)
    merge_sort_impl(arr, temp, mid + 1, right)
    merge(arr, temp, left, mid, right)

if __name__ == "__main__":
    n = SIZES[sys.argv[1]]
    arr = [n - i for i in range(n)]
    temp = [0] * n
    if n > 1:
        merge_sort_impl(arr, temp, 0, n - 1)
    print(arr[n - 1])
