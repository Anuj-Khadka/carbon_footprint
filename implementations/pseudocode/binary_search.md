## Binary Search

```
N    = 1,000,000
REPS = 1,000
arr  = [0, 2, 4, ..., (N-1)*2]   // sorted even numbers
target = (N-1) * 2

repeat REPS times:
    lo = 0
    hi = N - 1
    while lo <= hi:
        mid = (lo + hi) / 2
        if arr[mid] == target:
            return mid
        else if arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1

print result
```
