## Breadth-First Search

*O(V^2)*


```
V = 1,000
adj[V][V] = all false
visited[V] = all false
queue[V]

function bfs(start):
    if start < 0 or start >= V:
        return 0

    visited = [false] * V
    head = 0
    tail = 0
    count = 0

    visited[start] = true
    queue[tail] = start
    tail = tail + 1

    while head < tail:
        cur = queue[head]
        head = head + 1
        count++

        for nb = 0 to V-1:
            if adj[cur][nb] and not visited[nb]:
                visited[nb] = true
                if tail < V:
                    queue[tail] = nb
                    tail = tail + 1

    return count

for i = 0 to V-2:
    adj[i][i+1] = true
    adj[i+1][i] = true

for i = 0 to V-1 step 10:
    j = (i * 7 + 3) % V
    adj[i][j] = true
    adj[j][i] = true

print bfs(0)
```
