use std::env;

const SMALL: usize  = 100;
const MEDIUM: usize = 1000;
const LARGE: usize  = 5000;

fn bfs(adj: &Vec<Vec<bool>>, start: usize, v: usize) -> usize {
    let mut visited = vec![false; v];
    let mut queue = vec![0usize; v];
    let (mut head, mut tail, mut count) = (0, 0, 0);
    visited[start] = true;
    queue[tail] = start;
    tail += 1;
    while head < tail {
        let cur = queue[head];
        head += 1;
        count += 1;
        for nb in 0..v {
            if adj[cur][nb] && !visited[nb] {
                visited[nb] = true;
                queue[tail] = nb;
                tail += 1;
            }
        }
    }
    count
}

fn build_graph(v: usize) -> Vec<Vec<bool>> {
    let mut adj = vec![vec![false; v]; v];
    for i in 0..v - 1 {
        adj[i][i + 1] = true;
        adj[i + 1][i] = true;
    }
    let mut i = 0;
    while i < v {
        let j = (i * 7 + 3) % v;
        adj[i][j] = true;
        adj[j][i] = true;
        i += 10;
    }
    adj
}

fn main() {
    let args: Vec<String> = env::args().collect();
    let v = match args[1].as_str() {
        "small"  => SMALL,
        "medium" => MEDIUM,
        "large"  => LARGE,
        _ => { eprintln!("Unknown size: {}", args[1]); return; }
    };
    let adj = build_graph(v);
    println!("{}", bfs(&adj, 0, v));
}
