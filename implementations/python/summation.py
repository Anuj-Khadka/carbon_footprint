import sys

SMALL  = 100
MEDIUM = 10000
LARGE  = 1000000

SIZES = {"small": SMALL, "medium": MEDIUM, "large": LARGE}

def summation(arr, n):
    total = 0
    for i in range(n):
        total += arr[i]
    return total

if __name__ == "__main__":
    n = SIZES[sys.argv[1]]
    arr = [i + 1 for i in range(n)]
    print(summation(arr, n))
