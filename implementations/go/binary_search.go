package main

import "fmt"

const N    = 1_000_000
const REPS = 1_000

func binarySearch(arr []int64, target int64) int {
	lo, hi := 0, len(arr)-1
	for lo <= hi {
		mid := lo + (hi-lo)/2
		if arr[mid] == target {
			return mid
		} else if arr[mid] < target {
			lo = mid + 1
		} else {
			hi = mid - 1
		}
	}
	return -1
}

func main() {
	arr := make([]int64, N)
	for i := range arr {
		arr[i] = int64(i) * 2
	}
	target := int64(N-1) * 2
	result := -1
	for r := 0; r < REPS; r++ {
		result = binarySearch(arr, target)
	}
	fmt.Println(result)
}
