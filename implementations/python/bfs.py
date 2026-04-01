V = 1000

adj = [[False] * V for _ in range(V)]


def bfs(start):
    if start < 0 or start >= V:
        return 0

    visited = [False] * V
    queue = [0] * V
    head = 0
    tail = 0
    count = 0

    visited[start] = True
    queue[tail] = start
    tail += 1

    while head < tail:
        cur = queue[head]
        head += 1
        count += 1

        for nb in range(V):
            if adj[cur][nb] and not visited[nb]:
                visited[nb] = True
                if tail < V:
                    queue[tail] = nb
                    tail += 1

    return count


for i in range(V - 1):
    adj[i][i + 1] = True
    adj[i + 1][i] = True

for i in range(0, V, 10):
    j = (i * 7 + 3) % V
    adj[i][j] = True
    adj[j][i] = True

print(bfs(0))
