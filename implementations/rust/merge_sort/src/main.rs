const N: usize = 1_000_000;

thread_local! {
    static TEMP: std::cell::RefCell<Vec<i64>> = std::cell::RefCell::new(vec![0i64; N]);
}

fn merge_once_buffer(arr: &mut [i64], temp: &mut [i64], left: usize, mid: usize, right: usize) {
    for i in left..=right {
        temp[i] = arr[i];
    }

    let (mut i, mut j, mut k) = (left, mid + 1, left);

    while i <= mid && j <= right {
        if temp[i] <= temp[j] {
            arr[k] = temp[i];
            i += 1;
        } else {
            arr[k] = temp[j];
            j += 1;
        }
        k += 1;
    }

    while i <= mid {
        arr[k] = temp[i];
        i += 1;
        k += 1;
    }

    while j <= right {
        arr[k] = temp[j];
        j += 1;
        k += 1;
    }
}

fn merge_sort_impl(arr: &mut [i64], temp: &mut [i64], left: usize, right: usize) {
    if left >= right {
        return;
    }
    let mid = left + (right - left) / 2;
    merge_sort_impl(arr, temp, left, mid);
    merge_sort_impl(arr, temp, mid + 1, right);
    merge_once_buffer(arr, temp, left, mid, right);
}

fn merge_sort(arr: &mut [i64], n: usize) {
    if n < 2 {
        return;
    }
    TEMP.with(|t| {
        let mut temp = t.borrow_mut();
        merge_sort_impl(arr, &mut temp, 0, n - 1);
    });
}

fn main() {
    let mut arr = vec![0i64; N];
    for i in 0..N {
        arr[i] = (N - i) as i64;
    }
    merge_sort(&mut arr, N);
    println!("{}", arr[N - 1]);
}
