const N: usize = 300;

fn main() {
    let mut a = vec![0.0f64; N * N];
    let mut b = vec![0.0f64; N * N];
    let mut c = vec![0.0f64; N * N];

    for i in 0..N {
        for j in 0..N {
            a[i * N + j] = (i + j) as f64;
            b[i * N + j] = (i as i64 - j as i64) as f64;
        }
    }

    for i in 0..N {
        for j in 0..N {
            for k in 0..N {
                c[i * N + j] += a[i * N + k] * b[k * N + j];
            }
        }
    }

    println!("{:.2}", c[N / 2 * N + N / 2]);
}
