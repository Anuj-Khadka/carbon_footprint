use std::env;

const SMALL: usize  = 100;
const MEDIUM: usize = 10000;
const LARGE: usize  = 1000000;

fn summation(arr: &[i64], n: usize) -> i64 {
    let mut sum: i64 = 0;
    for i in 0..n {
        sum += arr[i];
    }
    sum
}

fn main() {
    let args: Vec<String> = env::args().collect();
    let n = match args[1].as_str() {
        "small"  => SMALL,
        "medium" => MEDIUM,
        "large"  => LARGE,
        _ => { eprintln!("Unknown size: {}", args[1]); return; }
    };
    let mut arr = vec![0i64; n];
    for i in 0..n {
        arr[i] = i as i64 + 1;
    }
    println!("{}", summation(&arr, n));
}
