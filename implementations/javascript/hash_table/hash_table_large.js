const readline = require('readline');

const N          = 100000;
const TABLE_SIZE = 150001;

const keys     = new Array(TABLE_SIZE).fill(0);
const vals     = new Array(TABLE_SIZE).fill(0);
const occupied = new Array(TABLE_SIZE).fill(false);

function setup() {
    // reset handles initialization
}

function hash_fn(key) {
    return Number(BigInt(key) * 2654435761n & 0xFFFFFFFFFFFFFFFFn) % TABLE_SIZE;
}

function insert(key, val) {
    let i = hash_fn(key);
    while (occupied[i]) {
        if (keys[i] === key) { vals[i] = val; return; }
        i = (i + 1) % TABLE_SIZE;
    }
    keys[i]     = key;
    vals[i]     = val;
    occupied[i] = true;
}

function lookup(key) {
    let i = hash_fn(key);
    while (occupied[i]) {
        if (keys[i] === key) return vals[i];
        i = (i + 1) % TABLE_SIZE;
    }
    return -1;
}

function reset() {
    for (let i = 0; i < TABLE_SIZE; i++) occupied[i] = false;
    for (let i = 0; i < N; i++) insert(i * 7 + 3, i * 13 + 5);
}

function hash_table() {
    reset();
    let checksum = 0;
    for (let i = 0; i < N; i++) checksum += lookup(i * 7 + 3);
    return checksum;
}

setup();
process.stdout.write("ready\n");

const rl = readline.createInterface({ input: process.stdin });
rl.on('line', () => {
    process.stdout.write(String(hash_table()) + "\n");
});