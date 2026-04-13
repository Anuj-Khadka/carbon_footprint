use std::io::{self, BufRead, Write};

const N: usize = 100;

static mut ARR: [i64; N] = [0; N];

fn setup() { ... }
fn algorithm() -> i64 { ... }

fn main() {
    unsafe { setup(); }

    println!("ready");
    std::io::stdout().flush().unwrap();

    let stdin = io::stdin();
    for _ in stdin.lock().lines() {
        unsafe {
            println!("{}", algorithm());
        }
        std::io::stdout().flush().unwrap();
    }
}