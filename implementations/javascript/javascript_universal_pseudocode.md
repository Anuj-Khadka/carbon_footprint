```
const readline = require('readline');

const N = 100;

const arr = new Array(N).fill(0);

function setup() {
    // fill data
}

function algorithm() {
    // run algorithm
    // return checksum
}

const rl = readline.createInterface({ input: process.stdin });

setup();

process.stdout.write("ready\n");

rl.on('line', () => {
    process.stdout.write(String(algorithm()) + "\n");
});
```