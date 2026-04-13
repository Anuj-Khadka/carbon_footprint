use std::io::{self, BufRead, Write};

const N: usize = 500;

static mut A: [[i64; N]; N] = [[0; N]; N];
static mut B: [[i64; N]; N] = [[0; N]; N];
static mut C: [[i64; N]; N] = [[0; N]; N];

fn setup() {
    unsafe {
        for i in 0..N {
            for j in 0..N {
                A[i][j] = (i + j) as i64;
                B[i][j] = (i as i64) - (j as i64);
            }
        }
    }
}

fn matrix_mul() -> i64 {
    unsafe {
        for i in 0..N {
            for j in 0..N {
                let mut acc: i64 = 0;
                for k in 0..N {
                    acc += A[i][k] * B[k][j];
                }
                C[i][j] = acc;
            }
        }
        C[N / 2][N / 2]
    }
}

fn main() {
    setup();

    println!("ready");
    io::stdout().flush().unwrap();

    let stdin = io::stdin();
    for _ in stdin.lock().lines() {
        println!("{}", matrix_mul());
        io::stdout().flush().unwrap();
    }
}