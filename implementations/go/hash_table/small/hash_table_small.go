package main

import (
	"bufio"
	"fmt"
	"os"
)

const N = 100
const TableSize = 151

var keys [TableSize]int64
var vals [TableSize]int64
var occupied [TableSize]bool

func setup() {
	// reset handles initialization
}

func hashFn(key int64) int {
	return int((uint64(key)*2654435761)&0xFFFFFFFFFFFFFFFF) % TableSize
}

func insert(key, val int64) {
	i := hashFn(key)
	for occupied[i] {
		if keys[i] == key {
			vals[i] = val
			return
		}
		i = (i + 1) % TableSize
	}
	keys[i] = key
	vals[i] = val
	occupied[i] = true
}

func lookup(key int64) int64 {
	i := hashFn(key)
	for occupied[i] {
		if keys[i] == key {
			return vals[i]
		}
		i = (i + 1) % TableSize
	}
	return -1
}

func reset() {
	for i := 0; i < TableSize; i++ {
		occupied[i] = false
	}
	for i := 0; i < N; i++ {
		insert(int64(i)*7+3, int64(i)*13+5)
	}
}

func hashTable() int64 {
	reset()
	var checksum int64 = 0
	for i := 0; i < N; i++ {
		checksum += lookup(int64(i)*7 + 3)
	}
	return checksum
}

func main() {
	setup()

	fmt.Println("ready")

	scanner := bufio.NewScanner(os.Stdin)
	for scanner.Scan() {
		fmt.Println(hashTable())
	}
}
