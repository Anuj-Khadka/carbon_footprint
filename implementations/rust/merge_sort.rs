use std::env;

const SMALL: usize  = 100;
const MEDIUM: usize = 10000;
const LARGE: usize  = 1000000;

fn merge(arr: &mut [i64], temp: &mut [i64], left: usize, mid: usize, right: usize) {
    for i in left..=right {
        temp[i] = arr[i];
    }
    let (mut i, mut j, mut k) = (left, mid + 1, left);
    while i <= mid && j <= right {
        if temp[i] <= temp[j] {
            arr[k] = temp[i]; i += 1;
        } else {
            arr[k] = temp[j]; j += 1;
        }
        k += 1;
    }
    while i <= mid { arr[k] = temp[i]; i += 1; k += 1; }
    while j <= right { arr[k] = temp[j]; j += 1; k += 1; }
}

fn merge_sort_impl(arr: &mut [i64], temp: &mut [i64], left: usize, right: usize) {
    if left >= right { return; }
    let mid = left + (right - left) / 2;
    merge_sort_impl(arr, temp, left, mid);
    merge_sort_impl(arr, temp, mid + 1, right);
    merge(arr, temp, left, mid, right);
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
    for i in 0..n { arr[i] = (n - i) as i64; }
    let mut temp = vec![0i64; n];
    if n > 1 { merge_sort_impl(&mut arr, &mut temp, 0, n - 1); }
    println!("{}", arr[n - 1]);
}
