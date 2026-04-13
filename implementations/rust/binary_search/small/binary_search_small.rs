use std::io::{self, BufRead, Write};

const N: usize = 100;

static mut ARR: [i64; N] = [0; N];

fn setup() {
    unsafe {
        for i in 0..N {
            ARR[i] = (i as i64) * 2;
        }
    }
}

fn binary_search() -> i64 {
    unsafe {
        let target = (N as i64 - 1) * 2;
        let mut lo = 0i64;
        let mut hi = N as i64 - 1;
        while lo <= hi {
            let mid = lo + (hi - lo) / 2;
            if ARR[mid as usize] == target {
                return mid;
            } else if ARR[mid as usize] < target {
                lo = mid + 1;
            } else {
                hi = mid - 1;
            }
        }
        -1
    }
}

fn main() {
    setup();

    println!("ready");
    io::stdout().flush().unwrap();

    let stdin = io::stdin();
    for _ in stdin.lock().lines() {
        println!("{}", binary_search());
        io::stdout().flush().unwrap();
    }
}