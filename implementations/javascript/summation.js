const N = 10_000_000;

function summation(arr, n) {
    let sum = 0;
    for (let i = 0; i < n; i++) {
        sum += arr[i];
    }
    return sum;
}

const arr = new Array(N);
for (let i = 0; i < N; i++) {
    arr[i] = i + 1;
}

console.log(summation(arr, N));
