const N    = 1_000_000;
const REPS = 1_000;

function binarySearch(arr, target) {
    let lo = 0, hi = arr.length - 1;
    while (lo <= hi) {
        const mid = (lo + hi) >> 1;
        if      (arr[mid] === target) return mid;
        else if (arr[mid] <  target)  lo = mid + 1;
        else                          hi = mid - 1;
    }
    return -1;
}

const arr = new Array(N);
for (let i = 0; i < N; i++) arr[i] = i * 2;
const target = (N - 1) * 2;
let result = -1;
for (let r = 0; r < REPS; r++) result = binarySearch(arr, target);
console.log(result);
