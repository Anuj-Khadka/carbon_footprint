import sys

N = 100

arr = [0] * N

def setup():
    for i in range(N):
        arr[i] = i * 2

def binary_search():
    target = (N - 1) * 2
    lo, hi = 0, N - 1
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1

def main():
    setup()

    sys.stdout.write("ready\n")
    sys.stdout.flush()

    for line in sys.stdin:
        sys.stdout.write(str(binary_search()) + "\n")
        sys.stdout.flush()

if __name__ == "__main__":
    main()