const N: usize = 1_000_000;

fn merge(arr: &mut Vec<i64>, l: usize, m: usize, r: usize) {
    let left  = arr[l..=m].to_vec();
    let right = arr[m+1..=r].to_vec();
    let (mut i, mut j, mut k) = (0, 0, l);
    while i < left.len() && j < right.len() {
        if left[i] <= right[j] { arr[k] = left[i];  i += 1; }
        else                   { arr[k] = right[j]; j += 1; }
        k += 1;
    }
    while i < left.len()  { arr[k] = left[i];  i += 1; k += 1; }
    while j < right.len() { arr[k] = right[j]; j += 1; k += 1; }
}

fn merge_sort(arr: &mut Vec<i64>, l: usize, r: usize) {
    if l >= r { return; }
    let m = l + (r - l) / 2;
    merge_sort(arr, l, m);
    merge_sort(arr, m + 1, r);
    merge(arr, l, m, r);
}

fn main() {
    let mut arr: Vec<i64> = (0..N as i64).map(|i| N as i64 - i).collect();
    merge_sort(&mut arr, 0, N - 1);
    println!("{}", arr[N - 1]);
}
