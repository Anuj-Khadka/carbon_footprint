N = 1_000_000


def merge_once_buffer(arr, temp, left, mid, right):
    for i in range(left, right + 1):
        temp[i] = arr[i]

    i = left
    j = mid + 1
    k = left

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
    merge_once_buffer(arr, temp, left, mid, right)


def merge_sort(arr, n):
    if arr is None or n < 2:
        return
    temp = [0] * n
    merge_sort_impl(arr, temp, 0, n - 1)


arr = [N - i for i in range(N)]
merge_sort(arr, N)
print(arr[N - 1])
