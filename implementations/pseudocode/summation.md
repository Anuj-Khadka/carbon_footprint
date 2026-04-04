## Summation

**Complexity:** O(n)

**Input sizes:** small = 100, medium = 10,000, large = 1,000,000

### Data

```
arr[LARGE]          — static global array of int64
```

### Setup

```
for i = 0 to n-1:
    arr[i] = i + 1
```

### Algorithm

```
function summation(n):
    sum = 0
    for i = 0 to n-1:
        sum = sum + arr[i]
    return sum
```

### Main

```
n = parse_size(argv[1])     // small → 100, medium → 10000, large → 1000000
setup arr with n elements
print summation(n)
```

### Expected output

| Size   | Output         |
|--------|----------------|
| small  | 5050           |
| medium | 50005000       |
| large  | 500000500000   |
