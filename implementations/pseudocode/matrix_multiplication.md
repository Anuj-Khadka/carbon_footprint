## Matrix Multiplication

**Complexity:** O(n^3)

**Input sizes:** small = 50, medium = 200, large = 500

### Data

```
a[N_MAX][N_MAX]     — static global matrix of int64
b[N_MAX][N_MAX]     — static global matrix of int64
c[N_MAX][N_MAX]     — static global result matrix of int64
```

### Setup

```
function fill_matrices(n):
    for i = 0 to n-1:
        for j = 0 to n-1:
            a[i][j] = i + j
            b[i][j] = i - j
```

### Algorithm

```
function matrix_multiply(n):
    clear c to all zeros
    for i = 0 to n-1:
        for j = 0 to n-1:
            acc = 0
            for k = 0 to n-1:
                acc = acc + a[i][k] * b[k][j]
            c[i][j] = acc
```

### Main

```
n = parse_size(argv[1])     // small → 50, medium → 200, large → 500
fill_matrices(n)
matrix_multiply(n)
print c[n/2][n/2]
```

### Expected output

| Size   | Output    |
|--------|-----------|
| small  | 9175      |
| medium | 646700    |
| large  | 10291750  |
