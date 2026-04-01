const V: usize = 1000;

fn bfs(adj: &[[bool; V]; V], start: isize) -> usize {
    if start < 0 || start as usize >= V {
        return 0;
    }

    let mut visited = [false; V];
    let mut queue = [0usize; V];
    let mut head = 0usize;
    let mut tail = 0usize;
    let mut count = 0usize;

    let start_idx = start as usize;
    visited[start_idx] = true;
    queue[tail] = start_idx;
    tail += 1;

    while head < tail {
        let cur = queue[head];
        head += 1;
        count += 1;

        for nb in 0..V {
            if adj[cur][nb] && !visited[nb] {
                visited[nb] = true;
                if tail < V {
                    queue[tail] = nb;
                    tail += 1;
                }
            }
        }
    }

    count
}

fn main() {
    let mut adj = [[false; V]; V];

    for i in 0..(V - 1) {
        adj[i][i + 1] = true;
        adj[i + 1][i] = true;
    }

    for i in (0..V).step_by(10) {
        let j = (i * 7 + 3) % V;
        adj[i][j] = true;
        adj[j][i] = true;
    }

    println!("{}", bfs(&adj, 0));
}
