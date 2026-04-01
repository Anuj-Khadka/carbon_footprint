package main

import "fmt"

const N = 300

var a [N][N]int64
var b [N][N]int64
var c [N][N]int64

func matrixMultiply() {
	for i := 0; i < N; i++ {
		for j := 0; j < N; j++ {
			var acc int64 = 0
			for k := 0; k < N; k++ {
				acc += a[i][k] * b[k][j]
			}
			c[i][j] = acc
		}
	}
}

func main() {
	for i := 0; i < N; i++ {
		for j := 0; j < N; j++ {
			a[i][j] = int64(i + j)
			b[i][j] = int64(i - j)
		}
	}

	matrixMultiply()

	fmt.Println(c[N/2][N/2])
}
