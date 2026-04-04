package main

import (
	"fmt"
	"os"
)

const (
	SMALL  = 50
	MEDIUM = 200
	LARGE  = 500
)

func main() {
	sizes := map[string]int{"small": SMALL, "medium": MEDIUM, "large": LARGE}
	n := sizes[os.Args[1]]

	a := make([][]int64, n)
	b := make([][]int64, n)
	c := make([][]int64, n)
	for i := 0; i < n; i++ {
		a[i] = make([]int64, n)
		b[i] = make([]int64, n)
		c[i] = make([]int64, n)
		for j := 0; j < n; j++ {
			a[i][j] = int64(i + j)
			b[i][j] = int64(i - j)
		}
	}
	for i := 0; i < n; i++ {
		for j := 0; j < n; j++ {
			var acc int64
			for k := 0; k < n; k++ {
				acc += a[i][k] * b[k][j]
			}
			c[i][j] = acc
		}
	}
	fmt.Println(c[n/2][n/2])
}
