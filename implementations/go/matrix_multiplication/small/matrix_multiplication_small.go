package main

import (
	"bufio"
	"fmt"
	"os"
)

const N = 50

var a [N][N]int64
var b [N][N]int64
var c [N][N]int64

func setup() {
	for i := 0; i < N; i++ {
		for j := 0; j < N; j++ {
			a[i][j] = int64(i + j)
			b[i][j] = int64(i - j)
		}
	}
}

func matrixMul() int64 {
	for i := 0; i < N; i++ {
		for j := 0; j < N; j++ {
			var acc int64 = 0
			for k := 0; k < N; k++ {
				acc += a[i][k] * b[k][j]
			}
			c[i][j] = acc
		}
	}
	return c[N/2][N/2]
}

func main() {
	setup()

	fmt.Println("ready")

	scanner := bufio.NewScanner(os.Stdin)
	for scanner.Scan() {
		fmt.Println(matrixMul())
	}
}
