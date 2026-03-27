## Hash Table

```
TABLE_SIZE = 10007
N          = 100,000
table      = array of TABLE_SIZE empty buckets (chaining)

function hash(key):
    return (key * 2654435761) mod TABLE_SIZE

function insert(key, value):
    idx = hash(key)
    if key exists in table[idx]: update value
    else: prepend (key, value) to table[idx]

function delete(key):
    idx = hash(key)
    remove entry with matching key from table[idx]

for i in 0..N:
    insert(i, i*2)

for i in 0, 3, 6, ..., N-1:
    delete(i)

count = total entries remaining in table
print count
```
