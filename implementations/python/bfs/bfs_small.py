import sys
from collections import deque

N = 100

adj = [[False] * N for _ in range(N)]
visited = [False] * N

def setup():
    for i in range(N - 1):
        adj[i][i + 1] = True
        adj[i + 1][i] = True
    for i in range(0, N, 10):
        j = (i * 7 + 3) % N
        adj[i][j] = True
        adj[j][i] = True

def bfs():
    for i in range(N):
        visited[i] = False
    queue = deque()
    visited[0] = True
    queue.append(0)
    count = 0
    while queue:
        cur = queue.popleft()
        count += 1
        for nb in range(N):
            if adj[cur][nb] and not visited[nb]:
                visited[nb] = True
                queue.append(nb)
    return count

def main():
    setup()

    sys.stdout.write("ready\n")
    sys.stdout.flush()

    for line in sys.stdin:
        sys.stdout.write(str(bfs()) + "\n")
        sys.stdout.flush()

if __name__ == "__main__":
    main()