
const readline = require('readline');

const N = 500;
const a = Array.from({ length: N }, () => new Array(N).fill(0));
const b = Array.from({ length: N }, () => new Array(N).fill(0));
const c = Array.from({ length: N }, () => new Array(N).fill(0));

function setup() {
    for (let i = 0; i < N; i++) {
        for (let j = 0; j < N; j++) {
            a[i][j] = i + j;
            b[i][j] = i - j;
        }
    }
}

function matrix_mul() {
    for (let i = 0; i < N; i++) {
        for (let j = 0; j < N; j++) {
            let acc = 0;
            for (let k = 0; k < N; k++) {
                acc += a[i][k] * b[k][j];
            }
            c[i][j] = acc;
        }
    }
    return c[Math.floor(N / 2)][Math.floor(N / 2)];
}

setup();
process.stdout.write("ready\n");

const rl = readline.createInterface({ input: process.stdin });
rl.on('line', () => {
    process.stdout.write(String(matrix_mul()) + "\n");
});