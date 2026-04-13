package main

import (
	"bufio"
	"fmt"
	"os"
)

const N = 1000000

var arr [N]int64

func setup() {
	for i := 0; i < N; i++ {
		arr[i] = int64(i + 1)
	}
}

func summation() int64 {
	var sum int64 = 0
	for i := 0; i < N; i++ {
		sum += arr[i]
	}
	return sum
}

func main() {
	setup()

	fmt.Println("ready")

	scanner := bufio.NewScanner(os.Stdin)
	for scanner.Scan() {
		fmt.Println(summation())
	}
}
