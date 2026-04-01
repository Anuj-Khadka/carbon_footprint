N = 10_000_000


def summation(arr, n):
    total = 0
    for i in range(n):
        total += arr[i]
    return total


arr = [0] * N
for i in range(N):
    arr[i] = i + 1

print(summation(arr, N))
