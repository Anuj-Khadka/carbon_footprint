## Binary Search

**Complexity:** O(log n)

**Input sizes:** small = 100, medium = 10,000, large = 1,000,000

### Data (static globals)

```
N = <100 | 10000 | 1000000>
arr[N]                               // static array of int64
```

### Setup (runs once at startup)

```
function setup():
    for i = 0 to N-1:
        arr[i] = i * 2              // sorted even numbers: 0, 2, 4, ...
```

### Algorithm (runs each time harness sends a trigger)

```
function binary_search():
    target = (N - 1) * 2            // last element
    lo = 0
    hi = N - 1
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

### Main (interactive stdin/stdout protocol)

```
setup()
print "ready"
flush stdout

while read line from stdin:
    print binary_search()
    flush stdout
```

### Expected output

| Size   | Output  |
|--------|---------|
| small  | 99      |
| medium | 9999    |
| large  | 999999  |
