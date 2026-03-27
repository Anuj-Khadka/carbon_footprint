## Matrix Multiplication

```
N = 300
A = N x N matrix where A[i][j] = i + j
B = N x N matrix where B[i][j] = i - j
C = N x N matrix of zeros

for i in 0..N:
    for j in 0..N:
        for k in 0..N:
            C[i][j] += A[i][k] * B[k][j]

print C[N/2][N/2]
```
