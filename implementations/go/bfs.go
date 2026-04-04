package main

import (
	"fmt"
	"os"
)

const (
	SMALL  = 100
	MEDIUM = 1000
	LARGE  = 5000
)

func bfs(adj [][]bool, start, v int) int {
	visited := make([]bool, v)
	queue := make([]int, v)
	head, tail, count := 0, 0, 0
	visited[start] = true
	queue[tail] = start
	tail++
	for head < tail {
		cur := queue[head]
		head++
		count++
		for nb := 0; nb < v; nb++ {
			if adj[cur][nb] && !visited[nb] {
				visited[nb] = true
				queue[tail] = nb
				tail++
			}
		}
	}
	return count
}

func buildGraph(v int) [][]bool {
	adj := make([][]bool, v)
	for i := range adj {
		adj[i] = make([]bool, v)
	}
	for i := 0; i < v-1; i++ {
		adj[i][i+1] = true
		adj[i+1][i] = true
	}
	for i := 0; i < v; i += 10 {
		j := (i*7 + 3) % v
		adj[i][j] = true
		adj[j][i] = true
	}
	return adj
}

func main() {
	sizes := map[string]int{"small": SMALL, "medium": MEDIUM, "large": LARGE}
	v := sizes[os.Args[1]]
	adj := buildGraph(v)
	fmt.Println(bfs(adj, 0, v))
}
