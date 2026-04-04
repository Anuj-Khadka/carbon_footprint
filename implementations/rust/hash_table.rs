use std::env;

const SMALL: usize      = 100;
const MEDIUM: usize     = 10000;
const LARGE: usize      = 100000;
const TABLE_SIZE: usize = 150001;

static mut KEYS: [i64; TABLE_SIZE] = [0; TABLE_SIZE];
static mut VALS: [i64; TABLE_SIZE] = [0; TABLE_SIZE];
static mut OCCUPIED: [bool; TABLE_SIZE] = [false; TABLE_SIZE];

fn hash(key: i64) -> usize {
    ((key as u64).wrapping_mul(2654435761) % TABLE_SIZE as u64) as usize
}

unsafe fn table_clear() {
    for i in 0..TABLE_SIZE { OCCUPIED[i] = false; }
}

unsafe fn insert(key: i64, val: i64) {
    let mut i = hash(key);
    while OCCUPIED[i] {
        if KEYS[i] == key { VALS[i] = val; return; }
        i = (i + 1) % TABLE_SIZE;
    }
    KEYS[i] = key;
    VALS[i] = val;
    OCCUPIED[i] = true;
}

unsafe fn lookup(key: i64) -> i64 {
    let mut i = hash(key);
    while OCCUPIED[i] {
        if KEYS[i] == key { return VALS[i]; }
        i = (i + 1) % TABLE_SIZE;
    }
    -1
}

fn main() {
    let args: Vec<String> = env::args().collect();
    let n = match args[1].as_str() {
        "small"  => SMALL,
        "medium" => MEDIUM,
        "large"  => LARGE,
        _ => { eprintln!("Unknown size: {}", args[1]); return; }
    };
    unsafe {
        table_clear();
        for i in 0..n {
            insert(i as i64 * 7 + 3, i as i64 * 13 + 5);
        }
        let mut checksum: i64 = 0;
        for i in 0..n {
            checksum += lookup(i as i64 * 7 + 3);
        }
        println!("{}", checksum);
    }
}
