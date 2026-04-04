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

func binarySearch(arr []int64, n int, target int64) int {
	lo, hi := 0, n-1
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
	sizes := map[string]int{"small": SMALL, "medium": MEDIUM, "large": LARGE}
	n := sizes[os.Args[1]]
	arr := make([]int64, n)
	for i := 0; i < n; i++ {
		arr[i] = int64(i) * 2
	}
	target := int64(n-1) * 2
	fmt.Println(binarySearch(arr, n, target))
}
