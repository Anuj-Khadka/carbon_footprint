const SIZES = { small: 100, medium: 10000, large: 1000000 };
const n = SIZES[process.argv[2]];

function merge(arr, temp, left, mid, right) {
    for (let i = left; i <= right; i++) temp[i] = arr[i];
    let i = left, j = mid + 1, k = left;
    while (i <= mid && j <= right)
        arr[k++] = temp[i] <= temp[j] ? temp[i++] : temp[j++];
    while (i <= mid) arr[k++] = temp[i++];
    while (j <= right) arr[k++] = temp[j++];
}

function mergeSortImpl(arr, temp, left, right) {
    if (left >= right) return;
    const mid = left + Math.floor((right - left) / 2);
    mergeSortImpl(arr, temp, left, mid);
    mergeSortImpl(arr, temp, mid + 1, right);
    merge(arr, temp, left, mid, right);
}

const arr = new Array(n);
for (let i = 0; i < n; i++) arr[i] = n - i;
const temp = new Array(n);
if (n > 1) mergeSortImpl(arr, temp, 0, n - 1);
console.log(arr[n - 1]);
