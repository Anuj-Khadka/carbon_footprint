use std::io::{self, BufRead, Write};

const N: usize = 100;

static mut ARR: [i64; N] = [0; N];

fn setup() {
    unsafe {
        for i in 0..N {
            ARR[i] = (i + 1) as i64;
        }
    }
}

fn summation() -> i64 {
    unsafe {
        let mut sum: i64 = 0;
        for i in 0..N {
            sum += ARR[i];
        }
        sum
    }
}

fn main() {
    setup();

    println!("ready");
    io::stdout().flush().unwrap();

    let stdin = io::stdin();
    for _ in stdin.lock().lines() {
        println!("{}", summation());
        io::stdout().flush().unwrap();
    }
}