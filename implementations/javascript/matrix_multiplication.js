const N = 300;

const A = Array.from({ length: N }, (_, i) => Array.from({ length: N }, (_, j) => i + j));
const B = Array.from({ length: N }, (_, i) => Array.from({ length: N }, (_, j) => i - j));
const C = Array.from({ length: N }, () => new Array(N).fill(0));

for (let i = 0; i < N; i++)
    for (let j = 0; j < N; j++)
        for (let k = 0; k < N; k++)
            C[i][j] += A[i][k] * B[k][j];

console.log(C[Math.floor(N / 2)][Math.floor(N / 2)].toFixed(2));
