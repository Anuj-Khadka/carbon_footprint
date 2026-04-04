## Breadth-First Search

**Complexity:** O(V^2) due to adjacency matrix

**Input sizes:** small = 100, medium = 1,000, large = 5,000

### Data

```
adj[V_MAX][V_MAX]   — static global adjacency matrix (bool)
visited[V_MAX]      — static global visited array (bool)
queue[V_MAX]        — static global BFS queue (int)
```

### Graph construction

```
function build_graph(v):
    clear adj to all false

    // Chain: 0—1—2—...—(v-1)
    for i = 0 to v-2:
        adj[i][i+1] = true
        adj[i+1][i] = true

    // Cross edges every 10 vertices
    for i = 0 to v-1 step 10:
        j = (i * 7 + 3) mod v
        adj[i][j] = true
        adj[j][i] = true
```

### Algorithm

```
function bfs(start, v):
    clear visited[0..v-1] to false
    head = 0
    tail = 0
    count = 0

    visited[start] = true
    queue[tail] = start
    tail = tail + 1

    while head < tail:
        cur = queue[head]
        head = head + 1
        count = count + 1

        for nb = 0 to v-1:
            if adj[cur][nb] AND NOT visited[nb]:
                visited[nb] = true
                queue[tail] = nb
                tail = tail + 1

    return count
```

### Main

```
v = parse_size(argv[1])     // small → 100, medium → 1000, large → 5000
build_graph(v)
print bfs(0, v)
```

### Expected output

| Size   | Output |
|--------|--------|
| small  | 100    |
| medium | 1000   |
| large  | 5000   |
