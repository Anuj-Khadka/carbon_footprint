const N = 1_000_000;

function mergeSort(arr) {
    if (arr.length <= 1) return arr;
    const mid = arr.length >> 1;
    const L = mergeSort(arr.slice(0, mid));
    const R = mergeSort(arr.slice(mid));
    const result = [];
    let i = 0, j = 0;
    while (i < L.length && j < R.length) {
        if (L[i] <= R[j]) result.push(L[i++]);
        else               result.push(R[j++]);
    }
    while (i < L.length) result.push(L[i++]);
    while (j < R.length) result.push(R[j++]);
    return result;
}

const arr = [];
for (let i = N; i > 0; i--) arr.push(i);
const sorted = mergeSort(arr);
console.log(sorted[sorted.length - 1]);
