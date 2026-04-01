## Matrix Multiplication

*O(n^3)*

```
N = 300
a = N x N matrix of int64
b = N x N matrix of int64
c = N x N matrix of int64 (initialized to 0)

for i in 0..N-1:
    for j in 0..N-1:
        a[i][j] = i + j
        b[i][j] = i - j

function matrix_multiply():
    for i in 0..N-1:
        for j in 0..N-1:
            acc = 0
            for k in 0..N-1:
                acc += a[i][k] * b[k][j]
            c[i][j] = acc

matrix_multiply()
print c[N/2][N/2]
```
