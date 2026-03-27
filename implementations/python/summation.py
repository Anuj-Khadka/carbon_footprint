N = 10_000_000

def summation(arr):
    sum = 0
    for x in arr:
        sum += x
    return sum

arr = list(range(1, N + 1))
print(summation(arr))
