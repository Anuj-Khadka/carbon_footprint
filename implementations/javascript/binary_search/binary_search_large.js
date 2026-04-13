const readline = require('readline');

const N = 1000000;
const arr = new Array(N).fill(0);

function setup() {
    for (let i = 0; i < N; i++) {
        arr[i] = i * 2;
    }
}

function binary_search() {
    const target = (N - 1) * 2;
    let lo = 0, hi = N - 1;
    while (lo <= hi) {
        const mid = lo + Math.floor((hi - lo) / 2);
        if (arr[mid] === target)     return mid;
        else if (arr[mid] < target)  lo = mid + 1;
        else                         hi = mid - 1;
    }
    return -1;
}

setup();
process.stdout.write("ready\n");

const rl = readline.createInterface({ input: process.stdin });
rl.on('line', () => {
    process.stdout.write(String(binary_search()) + "\n");
});