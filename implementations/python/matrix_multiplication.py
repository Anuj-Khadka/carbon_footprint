N = 300

A = [[i + j for j in range(N)] for i in range(N)]
B = [[i - j for j in range(N)] for i in range(N)]
C = [[0] * N for _ in range(N)]


def matrix_multiply():
    for i in range(N):
        for j in range(N):
            acc = 0
            for k in range(N):
                acc += A[i][k] * B[k][j]
            C[i][j] = acc


matrix_multiply()

print(C[N // 2][N // 2])
