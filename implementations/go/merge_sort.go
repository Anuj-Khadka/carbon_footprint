package main

import "fmt"

const N = 1_000_000

var temp [N]int64

func mergeOnceBuffer(arr *[N]int64, left, mid, right int) {
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

func mergeSortImpl(arr *[N]int64, left, right int) {
	if left >= right {
		return
	}
	mid := left + (right-left)/2
	mergeSortImpl(arr, left, mid)
	mergeSortImpl(arr, mid+1, right)
	mergeOnceBuffer(arr, left, mid, right)
}

func mergeSort(arr *[N]int64, n int) {
	if arr == nil || n < 2 {
		return
	}
	mergeSortImpl(arr, 0, n-1)
}

func main() {
	var arr [N]int64
	for i := 0; i < N; i++ {
		arr[i] = int64(N - i)
	}
	mergeSort(&arr, N)
	fmt.Println(arr[N-1])
}
