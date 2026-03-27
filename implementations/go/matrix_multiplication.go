package main

import "fmt"

const N = 300

func main() {
	A := make([]float64, N*N)
	B := make([]float64, N*N)
	C := make([]float64, N*N)

	for i := 0; i < N; i++ {
		for j := 0; j < N; j++ {
			A[i*N+j] = float64(i + j)
			B[i*N+j] = float64(i - j)
		}
	}

	for i := 0; i < N; i++ {
		for j := 0; j < N; j++ {
			for k := 0; k < N; k++ {
				C[i*N+j] += A[i*N+k] * B[k*N+j]
			}
		}
	}

	fmt.Printf("%.2f\n", C[N/2*N+N/2])
}
