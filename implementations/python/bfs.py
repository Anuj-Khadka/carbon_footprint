from collections import deque

V = 10_000

adj = [[(i + 1) % V, (i * 7 + 3) % V] for i in range(V)]

def bfs(start):
    visited = [False] * V
    queue = deque([start])
    visited[start] = True
    count = 0
    while queue:
        cur = queue.popleft()
        count += 1
        for nb in adj[cur]:
            if not visited[nb]:
                visited[nb] = True
                queue.append(nb)
    return count

print(bfs(0))
