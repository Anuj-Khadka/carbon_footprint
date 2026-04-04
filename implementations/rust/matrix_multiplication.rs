use std::env;

const SMALL: usize  = 50;
const MEDIUM: usize = 200;
const LARGE: usize  = 500;

fn main() {
    let args: Vec<String> = env::args().collect();
    let n = match args[1].as_str() {
        "small"  => SMALL,
        "medium" => MEDIUM,
        "large"  => LARGE,
        _ => { eprintln!("Unknown size: {}", args[1]); return; }
    };
    let mut a = vec![vec![0i64; n]; n];
    let mut b = vec![vec![0i64; n]; n];
    let mut c = vec![vec![0i64; n]; n];
    for i in 0..n {
        for j in 0..n {
            a[i][j] = (i + j) as i64;
            b[i][j] = i as i64 - j as i64;
        }
    }
    for i in 0..n {
        for j in 0..n {
            let mut acc: i64 = 0;
            for k in 0..n { acc += a[i][k] * b[k][j]; }
            c[i][j] = acc;
        }
    }
    println!("{}", c[n / 2][n / 2]);
}
