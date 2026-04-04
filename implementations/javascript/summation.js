const SIZES = { small: 100, medium: 10000, large: 1000000 };
const n = SIZES[process.argv[2]];

function summation(arr, n) {
    let sum = 0;
    for (let i = 0; i < n; i++) sum += arr[i];
    return sum;
}

const arr = new Array(n);
for (let i = 0; i < n; i++) arr[i] = i + 1;
console.log(summation(arr, n));
