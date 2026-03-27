N = 300

A = [[i + j for j in range(N)] for i in range(N)]
B = [[i - j for j in range(N)] for i in range(N)]
C = [[0.0] * N for _ in range(N)]

for i in range(N):
    for j in range(N):
        for k in range(N):
            C[i][j] += A[i][k] * B[k][j]

print(f"{C[N//2][N//2]:.2f}")
