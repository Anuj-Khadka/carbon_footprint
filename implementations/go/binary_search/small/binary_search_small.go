package main

import (
	"bufio"
	"fmt"
	"os"
)

const N = 100

var arr [N]int64

func setup() {
	for i := 0; i < N; i++ {
		arr[i] = int64(i) * 2
	}
}

func binarySearch() int {
	target := int64(N-1) * 2
	lo, hi := 0, N-1
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
	setup()

	fmt.Println("ready")

	scanner := bufio.NewScanner(os.Stdin)
	for scanner.Scan() {
		fmt.Println(binarySearch())
	}
}
