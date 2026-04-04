package main

import (
	"fmt"
	"os"
)

const (
	SMALL      = 100
	MEDIUM     = 10000
	LARGE      = 100000
	TABLE_SIZE = 150001
)

var (
	keys     [TABLE_SIZE]int64
	vals     [TABLE_SIZE]int64
	occupied [TABLE_SIZE]bool
)

func tableClear() {
	for i := range occupied {
		occupied[i] = false
	}
}

func hash(key int64) int {
	return int(uint64(key) * 2654435761 % TABLE_SIZE)
}

func insert(key, val int64) {
	i := hash(key)
	for occupied[i] {
		if keys[i] == key {
			vals[i] = val
			return
		}
		i = (i + 1) % TABLE_SIZE
	}
	keys[i] = key
	vals[i] = val
	occupied[i] = true
}

func lookup(key int64) int64 {
	i := hash(key)
	for occupied[i] {
		if keys[i] == key {
			return vals[i]
		}
		i = (i + 1) % TABLE_SIZE
	}
	return -1
}

func main() {
	sizes := map[string]int{"small": SMALL, "medium": MEDIUM, "large": LARGE}
	n := sizes[os.Args[1]]
	tableClear()
	for i := 0; i < n; i++ {
		insert(int64(i)*7+3, int64(i)*13+5)
	}
	var checksum int64
	for i := 0; i < n; i++ {
		checksum += lookup(int64(i)*7 + 3)
	}
	fmt.Println(checksum)
}
