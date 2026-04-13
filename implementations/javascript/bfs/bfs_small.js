
const SIZES = { small: 100, medium: 1000, large: 5000 };
const v = SIZES[process.argv[2]];

function bfs(adj, start, v) {
    const visited = new Uint8Array(v);
    const queue = new Int32Array(v);
    let head = 0, tail = 0, count = 0;
    visited[start] = 1;
    queue[tail++] = start;
    while (head < tail) {
        const cur = queue[head++];
        count++;
        for (let nb = 0; nb < v; nb++) {
            if (adj[cur][nb] && !visited[nb]) {
                visited[nb] = 1;
                queue[tail++] = nb;
            }
        }
    }
    return count;
}

const adj = Array.from({ length: v }, () => new Uint8Array(v));
for (let i = 0; i < v - 1; i++) {
    adj[i][i + 1] = 1;
    adj[i + 1][i] = 1;
}
for (let i = 0; i < v; i += 10) {
    const j = (i * 7 + 3) % v;
    adj[i][j] = 1;
    adj[j][i] = 1;
}
console.log(bfs(adj, 0, v));
