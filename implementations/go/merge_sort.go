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

func merge(arr, temp []int64, left, mid, right int) {
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

func mergeSortImpl(arr, temp []int64, left, right int) {
	if left >= right {
		return
	}
	mid := left + (right-left)/2
	mergeSortImpl(arr, temp, left, mid)
	mergeSortImpl(arr, temp, mid+1, right)
	merge(arr, temp, left, mid, right)
}

func main() {
	sizes := map[string]int{"small": SMALL, "medium": MEDIUM, "large": LARGE}
	n := sizes[os.Args[1]]
	arr := make([]int64, n)
	for i := 0; i < n; i++ {
		arr[i] = int64(n - i)
	}
	temp := make([]int64, n)
	if n > 1 {
		mergeSortImpl(arr, temp, 0, n-1)
	}
	fmt.Println(arr[n-1])
}
