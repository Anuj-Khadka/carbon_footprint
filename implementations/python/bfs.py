import sys

SMALL  = 100
MEDIUM = 1000
LARGE  = 5000

SIZES = {"small": SMALL, "medium": MEDIUM, "large": LARGE}

def bfs(adj, start, v):
    visited = [False] * v
    queue = [0] * v
    head, tail, count = 0, 0, 0
    visited[start] = True
    queue[tail] = start
    tail += 1
    while head < tail:
        cur = queue[head]
        head += 1
        count += 1
        for nb in range(v):
            if adj[cur][nb] and not visited[nb]:
                visited[nb] = True
                queue[tail] = nb
                tail += 1
    return count

def build_graph(v):
    adj = [[False] * v for _ in range(v)]
    for i in range(v - 1):
        adj[i][i + 1] = True
        adj[i + 1][i] = True
    for i in range(0, v, 10):
        j = (i * 7 + 3) % v
        adj[i][j] = True
        adj[j][i] = True
    return adj

if __name__ == "__main__":
    v = SIZES[sys.argv[1]]
    adj = build_graph(v)
    print(bfs(adj, 0, v))
