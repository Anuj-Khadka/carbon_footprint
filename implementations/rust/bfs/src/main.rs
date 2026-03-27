use std::collections::VecDeque;

const V: usize = 10_000;

fn bfs(adj: &[[usize; 2]], start: usize) -> usize {
    let mut visited = vec![false; V];
    let mut queue = VecDeque::new();
    visited[start] = true;
    queue.push_back(start);
    let mut count = 0;
    while let Some(cur) = queue.pop_front() {
        count += 1;
        for &nb in &adj[cur] {
            if !visited[nb] { visited[nb] = true; queue.push_back(nb); }
        }
    }
    count
}

fn main() {
    let adj: Vec<[usize; 2]> = (0..V)
        .map(|i| [(i + 1) % V, (i * 7 + 3) % V])
        .collect();
    println!("{}", bfs(&adj, 0));
}
