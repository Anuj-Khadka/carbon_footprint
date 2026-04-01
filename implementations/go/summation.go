package main

import "fmt"

const N = 10_000_000

func summation(arr []int64, n int) int64 {
	var sum int64
	for i := 0; i < n; i++ {
		sum += arr[i]
	}
	return sum
}

func main() {
	arr := make([]int64, N)
	for i := 0; i < N; i++ {
		arr[i] = int64(i) + 1
	}
	fmt.Println(summation(arr, N))
}
