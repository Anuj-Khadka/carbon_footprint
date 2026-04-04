import sys

SMALL  = 50
MEDIUM = 200
LARGE  = 500

SIZES = {"small": SMALL, "medium": MEDIUM, "large": LARGE}

if __name__ == "__main__":
    n = SIZES[sys.argv[1]]
    a = [[i + j for j in range(n)] for i in range(n)]
    b = [[i - j for j in range(n)] for i in range(n)]
    c = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            acc = 0
            for k in range(n):
                acc += a[i][k] * b[k][j]
            c[i][j] = acc
    print(c[n // 2][n // 2])
