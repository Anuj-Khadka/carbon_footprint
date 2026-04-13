const readline = require('readline');

const N = 1000;
const adj = Array.from({ length: N }, () => new Array(N).fill(false));
const visited = new Array(N).fill(false);

function setup() {
    for (let i = 0; i < N - 1; i++) {
        adj[i][i + 1] = true;
        adj[i + 1][i] = true;
    }
    for (let i = 0; i < N; i += 10) {
        const j = (i * 7 + 3) % N;
        adj[i][j] = true;
        adj[j][i] = true;
    }
}

function bfs() {
    for (let i = 0; i < N; i++) visited[i] = false;
    const queue = [0];
    visited[0] = true;
    let head = 0, count = 0;
    while (head < queue.length) {
        const cur = queue[head++];
        count++;
        for (let nb = 0; nb < N; nb++) {
            if (adj[cur][nb] && !visited[nb]) {
                visited[nb] = true;
                queue.push(nb);
            }
        }
    }
    return count;
}

setup();
process.stdout.write("ready\n");

const rl = readline.createInterface({ input: process.stdin });
rl.on('line', () => {
    process.stdout.write(String(bfs()) + "\n");
});