use std::env;

const SMALL: usize  = 100;
const MEDIUM: usize = 10000;
const LARGE: usize  = 1000000;

fn binary_search(arr: &[i64], n: usize, target: i64) -> i32 {
    let (mut lo, mut hi) = (0i64, n as i64 - 1);
    while lo <= hi {
        let mid = lo + (hi - lo) / 2;
        if arr[mid as usize] == target { return mid as i32; }
        else if arr[mid as usize] < target { lo = mid + 1; }
        else { hi = mid - 1; }
    }
    -1
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
        arr[i] = i as i64 * 2;
    }
    let target = (n as i64 - 1) * 2;
    println!("{}", binary_search(&arr, n, target));
}
