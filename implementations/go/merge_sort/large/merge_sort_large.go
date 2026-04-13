package main

import (
	"bufio"
	"fmt"
	"os"
)

const N = 1000000

var arr [N]int64
var temp [N]int64

func setup() {
	// reset handles initialization
}

func reset() {
	for i := 0; i < N; i++ {
		arr[i] = int64(N - i)
	}
}

func merge(left, mid, right int) {
	for i := left; i <= right; i++ {
		temp[i] = arr[i]
	}
	i, j, k := left, mid+1, left
	for i <= mid && j <= right {
		if temp[i] <= temp[j] {
			arr[k] = temp[i]
			i++
		} else {
			arr[k] = temp[j]
			j++
		}
		k++
	}
	for i <= mid {
		arr[k] = temp[i]
		i++
		k++
	}
	for j <= right {
		arr[k] = temp[j]
		j++
		k++
	}
}

func mergeSortImpl(left, right int) {
	if left >= right {
		return
	}
	mid := left + (right-left)/2
	mergeSortImpl(left, mid)
	mergeSortImpl(mid+1, right)
	merge(left, mid, right)
}

func mergeSort() int64 {
	reset()
	mergeSortImpl(0, N-1)
	return arr[N-1]
}

func main() {
	setup()

	fmt.Println("ready")

	scanner := bufio.NewScanner(os.Stdin)
	for scanner.Scan() {
		fmt.Println(mergeSort())
	}
}
