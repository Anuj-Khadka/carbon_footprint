const TABLE_SIZE = 10007;
const N          = 100_000;

const table = Array.from({ length: TABLE_SIZE }, () => []);

function hashFn(key) { return (key * 2654435761) % TABLE_SIZE; }

function insert(key, value) {
    const idx = hashFn(key);
    for (const pair of table[idx]) {
        if (pair[0] === key) { pair[1] = value; return; }
    }
    table[idx].push([key, value]);
}

function del(key) {
    const idx = hashFn(key);
    const b = table[idx];
    for (let i = 0; i < b.length; i++) {
        if (b[i][0] === key) { b.splice(i, 1); return; }
    }
}

for (let i = 0; i < N; i++) insert(i, i * 2);
for (let i = 0; i < N; i += 3) del(i);

let count = 0;
for (const bucket of table) count += bucket.length;
console.log(count);
