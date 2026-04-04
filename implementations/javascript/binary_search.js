const SIZES = { small: 100, medium: 10000, large: 1000000 };
const n = SIZES[process.argv[2]];

function binarySearch(arr, n, target) {
    let lo = 0, hi = n - 1;
    while (lo <= hi) {
        const mid = lo + ((hi - lo) >> 1);
        if (arr[mid] === target) return mid;
        else if (arr[mid] < target) lo = mid + 1;
        else hi = mid - 1;
    }
    return -1;
}

const arr = new Array(n);
for (let i = 0; i < n; i++) arr[i] = i * 2;
const target = (n - 1) * 2;
console.log(binarySearch(arr, n, target));
