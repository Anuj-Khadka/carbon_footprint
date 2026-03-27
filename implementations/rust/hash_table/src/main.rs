const TABLE_SIZE: usize = 10007;
const N: usize          = 100_000;

fn hash_fn(key: i64) -> usize {
    (key as u64).wrapping_mul(2654435761) as usize % TABLE_SIZE
}

fn insert(table: &mut Vec<Vec<(i64, i64)>>, key: i64, value: i64) {
    let idx = hash_fn(key);
    for pair in table[idx].iter_mut() {
        if pair.0 == key { pair.1 = value; return; }
    }
    table[idx].push((key, value));
}

fn delete(table: &mut Vec<Vec<(i64, i64)>>, key: i64) {
    let idx = hash_fn(key);
    table[idx].retain(|p| p.0 != key);
}

fn main() {
    let mut table: Vec<Vec<(i64, i64)>> = vec![Vec::new(); TABLE_SIZE];
    for i in 0..N { insert(&mut table, i as i64, i as i64 * 2); }
    for i in (0..N).step_by(3) { delete(&mut table, i as i64); }
    let count: usize = table.iter().map(|b| b.len()).sum();
    println!("{}", count);
}
