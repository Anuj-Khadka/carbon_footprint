## Matrix Multiplication

**Complexity:** O(n^3)

**Input sizes:** small = 50, medium = 200, large = 500

### Data (static globals)

```
N = <50 | 200 | 500>
a[N][N]                              // static matrix of int64
b[N][N]                              // static matrix of int64
c[N][N]                              // static result matrix of int64
```

### Setup (runs once - fills input matrices)

```
function setup():
    for i = 0 to N-1:
        for j = 0 to N-1:
            a[i][j] = i + j
            b[i][j] = i - j
```

### Algorithm (runs each time harness sends a trigger)

```
function matrix_mul():
    clear c to all zeros
    for i = 0 to N-1:
        for j = 0 to N-1:
            acc = 0
            for k = 0 to N-1:
                acc = acc + a[i][k] * b[k][j]
            c[i][j] = acc
    return c[N/2][N/2]
```

### Main (interactive stdin/stdout protocol)

```
setup()
print "ready"
flush stdout

while read line from stdin:
    print matrix_mul()
    flush stdout
```

### Expected output

| Size   | Output    |
|--------|-----------|
| small  | 9175      |
| medium | 646700    |
| large  | 10291750  |
