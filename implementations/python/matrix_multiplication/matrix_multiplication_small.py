import sys

N = 50

a = [[0] * N for _ in range(N)]
b = [[0] * N for _ in range(N)]
c = [[0] * N for _ in range(N)]

def setup():
    for i in range(N):
        for j in range(N):
            a[i][j] = i + j
            b[i][j] = i - j

def matrix_mul():
    for i in range(N):
        for j in range(N):
            acc = 0
            for k in range(N):
                acc += a[i][k] * b[k][j]
            c[i][j] = acc
    return c[N // 2][N // 2]

def main():
    setup()

    sys.stdout.write("ready\n")
    sys.stdout.flush()

    for line in sys.stdin:
        sys.stdout.write(str(matrix_mul()) + "\n")
        sys.stdout.flush()

if __name__ == "__main__":
    main()