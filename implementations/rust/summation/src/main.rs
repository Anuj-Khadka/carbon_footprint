const N: usize = 10_000_000;

fn summation(arr: &[i64], n: usize) -> i64 {
    let mut sum = 0i64;
    for i in 0..n {
        sum += arr[i];
    }
    sum
}

fn main() {
    let mut arr = vec![0i64; N];
    for i in 0..N {
        arr[i] = i as i64 + 1;
    }

    println!("{}", summation(&arr, N));
}
