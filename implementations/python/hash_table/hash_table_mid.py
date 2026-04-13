import sys

N          = 10000
TABLE_SIZE = 15001

keys     = [0] * TABLE_SIZE
vals     = [0] * TABLE_SIZE
occupied = [False] * TABLE_SIZE

def setup():
    pass  # reset handles initialization

def hash_fn(key):
    return ((key * 2654435761) & 0xFFFFFFFFFFFFFFFF) % TABLE_SIZE

def insert(key, val):
    i = hash_fn(key)
    while occupied[i]:
        if keys[i] == key:
            vals[i] = val
            return
        i = (i + 1) % TABLE_SIZE
    keys[i]     = key
    vals[i]     = val
    occupied[i] = True

def lookup(key):
    i = hash_fn(key)
    while occupied[i]:
        if keys[i] == key:
            return vals[i]
        i = (i + 1) % TABLE_SIZE
    return -1

def reset():
    for i in range(TABLE_SIZE):
        occupied[i] = False
    for i in range(N):
        insert(i * 7 + 3, i * 13 + 5)

def hash_table():
    reset()
    checksum = 0
    for i in range(N):
        checksum += lookup(i * 7 + 3)
    return checksum

def main():
    setup()

    sys.stdout.write("ready\n")
    sys.stdout.flush()

    for line in sys.stdin:
        sys.stdout.write(str(hash_table()) + "\n")
        sys.stdout.flush()

if __name__ == "__main__":
    main()