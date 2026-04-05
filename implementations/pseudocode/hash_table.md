## Hash Table (Open Addressing, Linear Probing)

**Complexity:** O(n) amortized for n inserts + n lookups

**Input sizes and table sizes:**

| Size   | N       | TABLE_SIZE |
|--------|---------|------------|
| small  | 100     | 151        |
| medium | 10,000  | 15,001     |
| large  | 100,000 | 150,001    |

TABLE_SIZE is approximately 1.5x N (prime) to keep load factor low.

### Data (static globals)

```
N = <100 | 10000 | 100000>
TABLE_SIZE = <151 | 15001 | 150001>
keys[TABLE_SIZE]                     // static array of int64
vals[TABLE_SIZE]                     // static array of int64
occupied[TABLE_SIZE]                 // static array of bool
```

### Hash function

```
function hash(key):
    return (key * 2654435761) mod TABLE_SIZE    // unsigned 64-bit multiply
```

### Insert and Lookup (open addressing, linear probing)

```
function insert(key, val):
    i = hash(key)
    while occupied[i]:
        if keys[i] == key:
            vals[i] = val
            return
        i = (i + 1) mod TABLE_SIZE
    keys[i] = key
    vals[i] = val
    occupied[i] = true

function lookup(key):
    i = hash(key)
    while occupied[i]:
        if keys[i] == key:
            return vals[i]
        i = (i + 1) mod TABLE_SIZE
    return -1
```

### Reset (runs before each measured run - clears table and re-inserts)

```
function reset():
    for i = 0 to TABLE_SIZE-1:
        occupied[i] = false
    for i = 0 to N-1:
        insert(i * 7 + 3, i * 13 + 5)
```

### Algorithm (runs each time harness sends a trigger)

```
function hash_table():
    reset()
    checksum = 0
    for i = 0 to N-1:
        checksum = checksum + lookup(i * 7 + 3)
    return checksum
```

### Main (interactive stdin/stdout protocol)

```
print "ready"
flush stdout

while read line from stdin:
    print hash_table()
    flush stdout
```

### Expected output

| Size   | Output        |
|--------|---------------|
| small  | 64850         |
| medium | 649985000     |
| large  | 64999850000   |
