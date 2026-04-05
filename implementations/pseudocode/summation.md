## Summation

**Complexity:** O(n)

**Input sizes:** small = 100, medium = 10,000, large = 1,000,000

### Data (static globals)

```
N = <100 | 10000 | 1000000>        // compile-time constant per binary
arr[N]                               // static array of int64
```

### Setup (runs once at startup)

```
function setup():
    for i = 0 to N-1:
        arr[i] = i + 1
```

### Algorithm (runs each time harness sends a trigger)

```
function summation():
    sum = 0
    for i = 0 to N-1:
        sum = sum + arr[i]
    return sum
```

### Main (interactive stdin/stdout protocol)

```
setup()
print "ready"
flush stdout

while read line from stdin:
    print summation()
    flush stdout
```

### Expected output

| Size   | Output         |
|--------|----------------|
| small  | 5050           |
| medium | 50005000       |
| large  | 500000500000   |
