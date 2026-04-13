use std::io::{self, BufRead, Write};

const N:          usize = 10000;
const TABLE_SIZE: usize = 15001;

static mut KEYS:     [i64; TABLE_SIZE]  = [0; TABLE_SIZE];
static mut VALS:     [i64; TABLE_SIZE]  = [0; TABLE_SIZE];
static mut OCCUPIED: [bool; TABLE_SIZE] = [false; TABLE_SIZE];

fn setup() {
    // reset handles initialization
}

fn hash_fn(key: i64) -> usize {
    ((key as u64).wrapping_mul(2654435761) & 0xFFFFFFFFFFFFFFFF) as usize % TABLE_SIZE
}

fn insert(key: i64, val: i64) {
    unsafe {
        let mut i = hash_fn(key);
        while OCCUPIED[i] {
            if KEYS[i] == key {
                VALS[i] = val;
                return;
            }
            i = (i + 1) % TABLE_SIZE;
        }
        KEYS[i]     = key;
        VALS[i]     = val;
        OCCUPIED[i] = true;
    }
}

fn lookup(key: i64) -> i64 {
    unsafe {
        let mut i = hash_fn(key);
        while OCCUPIED[i] {
            if KEYS[i] == key {
                return VALS[i];
            }
            i = (i + 1) % TABLE_SIZE;
        }
        -1
    }
}

fn reset() {
    unsafe {
        for i in 0..TABLE_SIZE {
            OCCUPIED[i] = false;
        }
    }
    for i in 0..N {
        insert(i as i64 * 7 + 3, i as i64 * 13 + 5);
    }
}

fn hash_table() -> i64 {
    reset();
    let mut checksum: i64 = 0;
    for i in 0..N {
        checksum += lookup(i as i64 * 7 + 3);
    }
    checksum
}

fn main() {
    setup();

    println!("ready");
    io::stdout().flush().unwrap();

    let stdin = io::stdin();
    for _ in stdin.lock().lines() {
        println!("{}", hash_table());
        io::stdout().flush().unwrap();
    }
}