package main

import "fmt"

const N = 10_000_000

func summation(arr []int64) int64 {
	var sum int64
	for _, v := range arr {
		sum += v
	}
	return sum
}

func main() {
	arr := make([]int64, N)
	for i := range arr {
		arr[i] = int64(i) + 1
	}
	fmt.Println(summation(arr))
}
