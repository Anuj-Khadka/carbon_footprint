package main

import "fmt"

const N = 1_000_000

func merge(arr []int64, l, m, r int) {
	L := make([]int64, m-l+1)
	R := make([]int64, r-m)
	copy(L, arr[l:m+1])
	copy(R, arr[m+1:r+1])
	i, j, k := 0, 0, l
	for i < len(L) && j < len(R) {
		if L[i] <= R[j] {
			arr[k] = L[i]; i++
		} else {
			arr[k] = R[j]; j++
		}
		k++
	}
	for i < len(L) { arr[k] = L[i]; i++; k++ }
	for j < len(R) { arr[k] = R[j]; j++; k++ }
}

func mergeSort(arr []int64, l, r int) {
	if l >= r {
		return
	}
	m := l + (r-l)/2
	mergeSort(arr, l, m)
	mergeSort(arr, m+1, r)
	merge(arr, l, m, r)
}

func main() {
	arr := make([]int64, N)
	for i := range arr {
		arr[i] = int64(N - i)
	}
	mergeSort(arr, 0, N-1)
	fmt.Println(arr[N-1])
}
