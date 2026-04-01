const N: usize    = 1_000_000;

fn binary_search(arr: &[i64], target: i64) -> i64 {
    let (mut lo, mut hi) = (0i64, arr.len() as i64 - 1);
    while lo <= hi {
        let mid = lo + (hi - lo) / 2;
        if arr[mid as usize] == target {
            return mid;
        } else if arr[mid as usize] < target {
            lo = mid + 1;
        } else {
            hi = mid - 1;
        }
    }
    -1
}

fn main() {
    let arr: Vec<i64> = (0..N as i64).map(|i| i * 2).collect();
    let target = (N as i64 - 1) * 2;
    let result = binary_search(&arr, target);
    println!("{}", result);
}
