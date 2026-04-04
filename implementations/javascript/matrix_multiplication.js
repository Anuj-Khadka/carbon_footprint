const SIZES = { small: 50, medium: 200, large: 500 };
const n = SIZES[process.argv[2]];

const a = Array.from({ length: n }, (_, i) => Array.from({ length: n }, (_, j) => i + j));
const b = Array.from({ length: n }, (_, i) => Array.from({ length: n }, (_, j) => i - j));
const c = Array.from({ length: n }, () => new Array(n).fill(0));

for (let i = 0; i < n; i++) {
    for (let j = 0; j < n; j++) {
        let acc = 0;
        for (let k = 0; k < n; k++) acc += a[i][k] * b[k][j];
        c[i][j] = acc;
    }
}

console.log(c[Math.floor(n / 2)][Math.floor(n / 2)]);
