const N: usize = 10_000_000;

fn summation(arr: &[i64]) -> i64 {
    arr.iter().sum()
}

fn main() {
    let arr: Vec<i64> = (1..=N as i64).collect();
    println!("{}", summation(&arr));
}
