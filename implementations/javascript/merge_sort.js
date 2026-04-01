const N = 1_000_000;

function mergeOnceBuffer(arr, temp, left, mid, right) {
    for (let i = left; i <= right; i++) {
        temp[i] = arr[i];
    }

    let i = left;
    let j = mid + 1;
    let k = left;

    while (i <= mid && j <= right) {
        arr[k++] = temp[i] <= temp[j] ? temp[i++] : temp[j++];
    }

    while (i <= mid) {
        arr[k++] = temp[i++];
    }

    while (j <= right) {
        arr[k++] = temp[j++];
    }
}

function mergeSortImpl(arr, temp, left, right) {
    if (left >= right) return;
    const mid = left + Math.floor((right - left) / 2);
    mergeSortImpl(arr, temp, left, mid);
    mergeSortImpl(arr, temp, mid + 1, right);
    mergeOnceBuffer(arr, temp, left, mid, right);
}

function mergeSort(arr, n) {
    if (arr === null || n < 2) return;
    const temp = new Array(n);
    mergeSortImpl(arr, temp, 0, n - 1);
}

const arr = new Array(N);
for (let i = 0; i < N; i++) {
    arr[i] = N - i;
}
mergeSort(arr, N);
console.log(arr[N - 1]);
