use std::io::{self, BufRead, Write};

const N: usize = 100;

static mut ADJ:     [[bool; N]; N] = [[false; N]; N];
static mut VISITED: [bool; N]      = [false; N];
static mut QUEUE:   [usize; N]     = [0; N];

fn setup() {
    unsafe {
        for i in 0..N - 1 {
            ADJ[i][i + 1] = true;
            ADJ[i + 1][i] = true;
        }
        for i in (0..N).step_by(10) {
            let j = (i * 7 + 3) % N;
            ADJ[i][j] = true;
            ADJ[j][i] = true;
        }
    }
}

fn bfs() -> usize {
    unsafe {
        for i in 0..N {
            VISITED[i] = false;
        }
        let mut head = 0;
        let mut tail = 0;
        let mut count = 0;
        VISITED[0]    = true;
        QUEUE[tail]   = 0;
        tail += 1;
        while head < tail {
            let cur = QUEUE[head];
            head += 1;
            count += 1;
            for nb in 0..N {
                if ADJ[cur][nb] && !VISITED[nb] {
                    VISITED[nb]  = true;
                    QUEUE[tail]  = nb;
                    tail += 1;
                }
            }
        }
        count
    }
}

fn main() {
    setup();

    println!("ready");
    io::stdout().flush().unwrap();

    let stdin = io::stdin();
    for _ in stdin.lock().lines() {
        println!("{}", bfs());
        io::stdout().flush().unwrap();
    }
}