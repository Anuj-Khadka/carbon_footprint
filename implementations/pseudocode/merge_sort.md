## Merge Sort

**Complexity:** O(n log n)

**Input sizes:** small = 100, medium = 10,000, large = 1,000,000

### Data

```
arr[LARGE]          — static global array of int64
temp[LARGE]         — static global temp buffer for merging
```

### Setup

```
for i = 0 to n-1:
    arr[i] = n - i            // reverse sorted: n, n-1, ..., 2, 1
```

### Algorithm

```
function merge(left, mid, right):
    // Copy segment to temp
    for i = left to right:
        temp[i] = arr[i]

    i = left
    j = mid + 1
    k = left

    // Merge back into arr
    while i <= mid AND j <= right:
        if temp[i] <= temp[j]:
            arr[k] = temp[i]
            i = i + 1
        else:
            arr[k] = temp[j]
            j = j + 1
        k = k + 1

    // Copy remaining left half
    while i <= mid:
        arr[k] = temp[i]
        i = i + 1
        k = k + 1

    // Copy remaining right half
    while j <= right:
        arr[k] = temp[j]
        j = j + 1
        k = k + 1


function merge_sort_impl(left, right):
    if left >= right:
        return
    mid = left + (right - left) / 2
    merge_sort_impl(left, mid)
    merge_sort_impl(mid + 1, right)
    merge(left, mid, right)
```

### Main

```
n = parse_size(argv[1])
fill arr with reverse-sorted data
if n > 1:
    merge_sort_impl(0, n - 1)
print arr[n - 1]
```

### Expected output

| Size   | Output   |
|--------|----------|
| small  | 100      |
| medium | 10000    |
| large  | 1000000  |
