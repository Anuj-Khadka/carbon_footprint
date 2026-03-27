TABLE_SIZE = 10007
N          = 100_000

table = [[] for _ in range(TABLE_SIZE)]

def hash_fn(key):
    return (key * 2654435761) % TABLE_SIZE

def insert(key, value):
    idx = hash_fn(key)
    for pair in table[idx]:
        if pair[0] == key:
            pair[1] = value
            return
    table[idx].append([key, value])

def delete(key):
    idx = hash_fn(key)
    table[idx] = [p for p in table[idx] if p[0] != key]

for i in range(N):
    insert(i, i * 2)
for i in range(0, N, 3):
    delete(i)

count = sum(len(bucket) for bucket in table)
print(count)
