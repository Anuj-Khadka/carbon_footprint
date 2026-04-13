use std::io::{self, BufRead, Write};

const N: usize = 10000;

static mut ARR:  [i64; N] = [0; N];
static mut TEMP: [i64; N] = [0; N];

fn setup() {
    // reset handles initialization
}

fn reset() {
    unsafe {
        for i in 0..N {
            ARR[i] = (N - i) as i64;
        }
    }
}

fn merge(left: usize, mid: usize, right: usize) {
    unsafe {
        for i in left..=right {
            TEMP[i] = ARR[i];
        }
        let mut i = left;
        let mut j = mid + 1;
        let mut k = left;
        while i <= mid && j <= right {
            if TEMP[i] <= TEMP[j] {
                ARR[k] = TEMP[i];
                i += 1;
            } else {
                ARR[k] = TEMP[j];
                j += 1;
            }
            k += 1;
        }
        while i <= mid {
            ARR[k] = TEMP[i];
            i += 1;
            k += 1;
        }
        while j <= right {
            ARR[k] = TEMP[j];
            j += 1;
            k += 1;
        }
    }
}

fn merge_sort_impl(left: usize, right: usize) {
    if left >= right {
        return;
    }
    let mid = left + (right - left) / 2;
    merge_sort_impl(left, mid);
    merge_sort_impl(mid + 1, right);
    merge(left, mid, right);
}

fn merge_sort() -> i64 {
    reset();
    merge_sort_impl(0, N - 1);
    unsafe { ARR[N - 1] }
}

fn main() {
    setup();

    println!("ready");
    io::stdout().flush().unwrap();

    let stdin = io::stdin();
    for _ in stdin.lock().lines() {
        println!("{}", merge_sort());
        io::stdout().flush().unwrap();
    }
}