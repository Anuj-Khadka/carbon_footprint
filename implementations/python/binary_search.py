N    = 1_000_000
REPS = 1_000

def binary_search(arr, target):
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if   arr[mid] == target: return mid
        elif arr[mid] <  target: lo = mid + 1
        else:                    hi = mid - 1
    return -1

arr    = [i * 2 for i in range(N)]
target = (N - 1) * 2
result = -1
for _ in range(REPS):
    result = binary_search(arr, target)
print(result)
