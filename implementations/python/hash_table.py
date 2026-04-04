import sys

SMALL      = 100
MEDIUM     = 10000
LARGE      = 100000
TABLE_SIZE = 150001

SIZES = {"small": SMALL, "medium": MEDIUM, "large": LARGE}

keys     = [0] * TABLE_SIZE
vals     = [0] * TABLE_SIZE
occupied = [False] * TABLE_SIZE

def table_clear():
    for i in range(TABLE_SIZE):
        occupied[i] = False

def hash_fn(key):
    return ((key * 2654435761) & 0xFFFFFFFFFFFFFFFF) % TABLE_SIZE

def insert(key, val):
    i = hash_fn(key)
    while occupied[i]:
        if keys[i] == key:
            vals[i] = val
            return
        i = (i + 1) % TABLE_SIZE
    keys[i] = key
    vals[i] = val
    occupied[i] = True

def lookup(key):
    i = hash_fn(key)
    while occupied[i]:
        if keys[i] == key:
            return vals[i]
        i = (i + 1) % TABLE_SIZE
    return -1

if __name__ == "__main__":
    n = SIZES[sys.argv[1]]
    table_clear()
    for i in range(n):
        insert(i * 7 + 3, i * 13 + 5)
    checksum = 0
    for i in range(n):
        checksum += lookup(i * 7 + 3)
    print(checksum)
