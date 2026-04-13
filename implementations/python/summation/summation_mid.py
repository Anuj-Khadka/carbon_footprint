import sys

N = 10000

arr = [0] * N

def setup():
    for i in range(N):
        arr[i] = i + 1

def summation():
    total = 0
    for i in range(N):
        total += arr[i]
    return total

def main():
    setup()

    sys.stdout.write("ready\n")
    sys.stdout.flush()

    for line in sys.stdin:
        sys.stdout.write(str(summation()) + "\n")
        sys.stdout.flush()

if __name__ == "__main__":
    main()