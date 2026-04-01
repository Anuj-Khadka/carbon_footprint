const V = 1000;

const adj = Array.from({ length: V }, () => new Uint8Array(V));

function bfs(start) {
    if (start < 0 || start >= V) {
        return 0;
    }

    const visited = new Uint8Array(V);
    const queue = new Int32Array(V);
    let head = 0;
    let tail = 0;
    let count = 0;

    visited[start] = 1;
    queue[tail++] = start;

    while (head < tail) {
        const cur = queue[head++];
        count++;

        for (let nb = 0; nb < V; nb++) {
            if (adj[cur][nb] && !visited[nb]) {
                visited[nb] = 1;
                if (tail < V) {
                    queue[tail++] = nb;
                }
            }
        }
    }

    return count;
}

for (let i = 0; i < V - 1; i++) {
    adj[i][i + 1] = 1;
    adj[i + 1][i] = 1;
}

for (let i = 0; i < V; i += 10) {
    const j = (i * 7 + 3) % V;
    adj[i][j] = 1;
    adj[j][i] = 1;
}

console.log(bfs(0));
