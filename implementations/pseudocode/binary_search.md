## Binary Search

**Complexity:** O(log n)

**Input sizes:** small = 100, medium = 10,000, large = 1,000,000

### Data

```
arr[LARGE]          — static global array of int64
```

### Setup

```
for i = 0 to n-1:
    arr[i] = i * 2           // sorted even numbers: 0, 2, 4, ...
target = (n - 1) * 2         // last element
```

### Algorithm

```
function binary_search(n, target):
    lo = 0
    hi = n - 1
    while lo <= hi:
        mid = lo + (hi - lo) / 2
        if arr[mid] == target:
            return mid
        else if arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
```

### Main

```
n = parse_size(argv[1])
setup arr and target
print binary_search(n, target)
```

### Expected output

| Size   | Output  |
|--------|---------|
| small  | 99      |
| medium | 9999    |
| large  | 999999  |
