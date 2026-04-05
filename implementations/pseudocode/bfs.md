## Breadth-First Search

**Complexity:** O(V^2) due to adjacency matrix

**Input sizes:** small = 100, medium = 1,000, large = 5,000

### Data (static globals)

```
N = <100 | 1000 | 5000>
adj[N][N]                            // static adjacency matrix (bool)
visited[N]                           // static visited array (bool)
queue[N]                             // static BFS queue (int)
```

### Setup (runs once - builds graph)

```
function setup():
    clear adj to all false

    // Chain: 0-1-2-...-(N-1)
    for i = 0 to N-2:
        adj[i][i+1] = true
        adj[i+1][i] = true

    // Cross edges every 10 vertices
    for i = 0 to N-1 step 10:
        j = (i * 7 + 3) mod N
        adj[i][j] = true
        adj[j][i] = true
```

### Algorithm (runs each time harness sends a trigger)

```
function bfs():
    clear visited to all false
    head = 0
    tail = 0
    count = 0

    visited[0] = true
    queue[tail] = 0
    tail = tail + 1

    while head < tail:
        cur = queue[head]
        head = head + 1
        count = count + 1

        for nb = 0 to N-1:
            if adj[cur][nb] AND NOT visited[nb]:
                visited[nb] = true
                queue[tail] = nb
                tail = tail + 1

    return count
```

### Main (interactive stdin/stdout protocol)

```
setup()
print "ready"
flush stdout

while read line from stdin:
    print bfs()
    flush stdout
```

### Expected output

| Size   | Output |
|--------|--------|
| small  | 100    |
| medium | 1000   |
| large  | 5000   |
