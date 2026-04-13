import sys

N = 1_000_000

arr = [0] * N

def setup():
    pass  # reset handles initialization

def reset():
    for i in range(N):
        arr[i] = N - i

def merge_sort_impl(left, right):
    if left >= right:
        return
    mid = left + (right - left) // 2
    merge_sort_impl(left, mid)
    merge_sort_impl(mid + 1, right)
    merge(left, mid, right)

def merge(left, mid, right):
    temp = arr[left:right + 1]
    i, j, k = 0, mid - left + 1, left
    while i <= mid - left and j <= right - left:
        if temp[i] <= temp[j]:
            arr[k] = temp[i]
            i += 1
        else:
            arr[k] = temp[j]
            j += 1
        k += 1
    while i <= mid - left:
        arr[k] = temp[i]
        i += 1
        k += 1
    while j <= right - left:
        arr[k] = temp[j]
        j += 1
        k += 1

def merge_sort():
    reset()
    merge_sort_impl(0, N - 1)
    return arr[N - 1]

def main():
    setup()

    sys.stdout.write("ready\n")
    sys.stdout.flush()

    for line in sys.stdin:
        sys.stdout.write(str(merge_sort()) + "\n")
        sys.stdout.flush()

if __name__ == "__main__":
    main()