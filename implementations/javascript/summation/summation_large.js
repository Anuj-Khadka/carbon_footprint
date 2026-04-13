
const readline = require('readline');

const N = 1000000;
const arr = new Array(N).fill(0);

function setup() {
    for (let i = 0; i < N; i++) {
        arr[i] = i + 1;
    }
}

function summation() {
    let sum = 0;
    for (let i = 0; i < N; i++) {
        sum += arr[i];
    }
    return sum;
}

setup();
process.stdout.write("ready\n");

const rl = readline.createInterface({ input: process.stdin });
rl.on('line', () => {
    process.stdout.write(String(summation()) + "\n");
});