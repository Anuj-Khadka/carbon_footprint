## Merge Sort

**Complexity:** O(n log n)

**Input sizes:** small = 100, medium = 10,000, large = 1,000,000

### Data (static globals)

```
N = <100 | 10000 | 1000000>
arr[N]                               // static array of int64
temp[N]                              // static temp buffer for merging
```

### Setup (runs once at startup - empty, no work needed)

```
function setup():
    // nothing - reset() handles per-run initialization
```

### Reset (runs before each sort to restore reverse-sorted data)

```
function reset():
    for i = 0 to N-1:
        arr[i] = N - i              // reverse sorted: N, N-1, ..., 2, 1
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
            arr[k] = temp[i];  i = i + 1
        else:
            arr[k] = temp[j];  j = j + 1
        k = k + 1

    while i <= mid:
        arr[k] = temp[i];  i = i + 1;  k = k + 1
    while j <= right:
        arr[k] = temp[j];  j = j + 1;  k = k + 1


function merge_sort_impl(left, right):
    if left >= right:
        return
    mid = left + (right - left) / 2
    merge_sort_impl(left, mid)
    merge_sort_impl(mid + 1, right)
    merge(left, mid, right)


function merge_sort():
    reset()
    merge_sort_impl(0, N - 1)
    return arr[N - 1]
```

### Main (interactive stdin/stdout protocol)

```
setup()
print "ready"
flush stdout

while read line from stdin:
    print merge_sort()
    flush stdout
```

### Expected output

| Size   | Output   |
|--------|----------|
| small  | 100      |
| medium | 10000    |
| large  | 1000000  |
