const SIZES = { small: 100, medium: 10000, large: 100000 };
const TABLE_SIZE = 150001;
const n = SIZES[process.argv[2]];

const keys     = new Float64Array(TABLE_SIZE);
const vals     = new Float64Array(TABLE_SIZE);
const occupied = new Uint8Array(TABLE_SIZE);

function hashFn(key) {
    return Number(BigInt(key) * 2654435761n % BigInt(TABLE_SIZE));
}

function insert(key, val) {
    let i = hashFn(key);
    while (occupied[i]) {
        if (keys[i] === key) { vals[i] = val; return; }
        i = (i + 1) % TABLE_SIZE;
    }
    keys[i] = key;
    vals[i] = val;
    occupied[i] = 1;
}

function lookup(key) {
    let i = hashFn(key);
    while (occupied[i]) {
        if (keys[i] === key) return vals[i];
        i = (i + 1) % TABLE_SIZE;
    }
    return -1;
}

for (let i = 0; i < n; i++) insert(i * 7 + 3, i * 13 + 5);
let checksum = 0;
for (let i = 0; i < n; i++) checksum += lookup(i * 7 + 3);
console.log(checksum);
