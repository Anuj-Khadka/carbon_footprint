const N: usize = 300;

fn matrix_multiply(a: &Vec<Vec<i64>>, b: &Vec<Vec<i64>>, c: &mut Vec<Vec<i64>>) {
    for i in 0..N {
        for j in 0..N {
            let mut acc = 0i64;
            for k in 0..N {
                acc += a[i][k] * b[k][j];
            }
            c[i][j] = acc;
        }
    }
}

fn main() {
    let mut a = vec![vec![0i64; N]; N];
    let mut b = vec![vec![0i64; N]; N];
    let mut c = vec![vec![0i64; N]; N];

    for i in 0..N {
        for j in 0..N {
            a[i][j] = (i + j) as i64;
            b[i][j] = i as i64 - j as i64;
        }
    }

    matrix_multiply(&a, &b, &mut c);

    println!("{}", c[N / 2][N / 2]);
}
