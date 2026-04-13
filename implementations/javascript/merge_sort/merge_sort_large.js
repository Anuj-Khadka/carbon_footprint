const readline = require('readline');

const N = 1000000;
const arr = new Array(N).fill(0);

function setup() {
    // reset handles initialization
}

function reset() {
    for (let i = 0; i < N; i++) {
        arr[i] = N - i;
    }
}

function merge(left, mid, right) {
    const temp = arr.slice(left, right + 1);
    let i = 0, j = mid - left + 1, k = left;
    while (i <= mid - left && j <= right - left) {
        if (temp[i] <= temp[j]) {
            arr[k++] = temp[i++];
        } else {
            arr[k++] = temp[j++];
        }
    }
    while (i <= mid - left) arr[k++] = temp[i++];
    while (j <= right - left) arr[k++] = temp[j++];
}

function merge_sort_impl(left, right) {
    if (left >= right) return;
    const mid = left + Math.floor((right - left) / 2);
    merge_sort_impl(left, mid);
    merge_sort_impl(mid + 1, right);
    merge(left, mid, right);
}

function merge_sort() {
    reset();
    merge_sort_impl(0, N - 1);
    return arr[N - 1];
}

setup();
process.stdout.write("ready\n");

const rl = readline.createInterface({ input: process.stdin });
rl.on('line', () => {
    process.stdout.write(String(merge_sort()) + "\n");
});