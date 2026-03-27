## Breadth-First Search

```
V   = 10,000
adj = graph where each node i connects to:
        (i+1) % V
        (i*7 + 3) % V

function bfs(start):
    visited = [false] * V
    queue   = [start]
    visited[start] = true
    count = 0
    while queue is not empty:
        cur = dequeue(queue)
        count++
        for each neighbor nb of cur:
            if not visited[nb]:
                visited[nb] = true
                enqueue(queue, nb)
    return count

print bfs(0)
```
