const V = 10_000;

const adj = [];
for (let i = 0; i < V; i++) adj.push([(i + 1) % V, (i * 7 + 3) % V]);

function bfs(start) {
    const visited = new Uint8Array(V);
    const queue = [start];
    visited[start] = 1;
    let head = 0, count = 0;
    while (head < queue.length) {
        const cur = queue[head++];
        count++;
        for (const nb of adj[cur]) {
            if (!visited[nb]) { visited[nb] = 1; queue.push(nb); }
        }
    }
    return count;
}

console.log(bfs(0));
