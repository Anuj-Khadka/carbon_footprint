## Hash Table (Open Addressing, Linear Probing)

**Complexity:** O(n) amortized for n inserts + n lookups

**Input sizes:** small = 100, medium = 10,000, large = 100,000
**Table size:** 150,001

### Data

```
keys[TABLE_SIZE]      — static global array of int64
vals[TABLE_SIZE]      — static global array of int64
occupied[TABLE_SIZE]  — static global array of bool
```

### Algorithm

```
function hash(key):
    return (key * 2654435761) mod TABLE_SIZE

function table_clear():
    set all occupied[] to false

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

### Main

```
n = parse_size(argv[1])
table_clear()

for i = 0 to n-1:
    insert(i * 7 + 3, i * 13 + 5)

checksum = 0
for i = 0 to n-1:
    checksum = checksum + lookup(i * 7 + 3)

print checksum
```

### Expected output

| Size   | Output        |
|--------|---------------|
| small  | 64850         |
| medium | 649985000     |
| large  | 64999850000   |
