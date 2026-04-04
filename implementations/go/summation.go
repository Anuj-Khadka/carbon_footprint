package main

import (
	"fmt"
	"os"
)

const (
	SMALL  = 100
	MEDIUM = 10000
	LARGE  = 1000000
)

func summation(arr []int64, n int) int64 {
	var sum int64
	for i := 0; i < n; i++ {
		sum += arr[i]
	}
	return sum
}

func main() {
	sizes := map[string]int{"small": SMALL, "medium": MEDIUM, "large": LARGE}
	n := sizes[os.Args[1]]
	arr := make([]int64, n)
	for i := 0; i < n; i++ {
		arr[i] = int64(i) + 1
	}
	fmt.Println(summation(arr, n))
}
