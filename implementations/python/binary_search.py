import sys

SMALL  = 100
MEDIUM = 10000
LARGE  = 1000000

SIZES = {"small": SMALL, "medium": MEDIUM, "large": LARGE}

def binary_search(arr, n, target):
    lo, hi = 0, n - 1
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1

if __name__ == "__main__":
    n = SIZES[sys.argv[1]]
    arr = [i * 2 for i in range(n)]
    target = (n - 1) * 2
    print(binary_search(arr, n, target))
