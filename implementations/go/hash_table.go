package main

import "fmt"

const TABLE_SIZE = 10007
const N          = 100_000

type Node struct {
	key, value int64
	next       *Node
}

var table [TABLE_SIZE]*Node

func hashFn(key int64) int {
	return int(uint64(key)*2654435761) % TABLE_SIZE
}

func insert(key, value int64) {
	idx := hashFn(key)
	for n := table[idx]; n != nil; n = n.next {
		if n.key == key { n.value = value; return }
	}
	table[idx] = &Node{key, value, table[idx]}
}

func delete(key int64) {
	idx := hashFn(key)
	n, prev := table[idx], (*Node)(nil)
	for n != nil {
		if n.key == key {
			if prev != nil { prev.next = n.next } else { table[idx] = n.next }
			return
		}
		prev, n = n, n.next
	}
}

func main() {
	for i := 0; i < N; i++ { insert(int64(i), int64(i)*2) }
	for i := 0; i < N; i += 3 { delete(int64(i)) }
	count := 0
	for _, n := range table {
		for ; n != nil; n = n.next { count++ }
	}
	fmt.Println(count)
}
