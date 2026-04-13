package main

import (
	"bufio"
	"fmt"
	"os"
)

const N = 1000

var adj [N][N]bool
var visited [N]bool
var queue [N]int

func setup() {
	for i := 0; i < N-1; i++ {
		adj[i][i+1] = true
		adj[i+1][i] = true
	}
	for i := 0; i < N; i += 10 {
		j := (i*7 + 3) % N
		adj[i][j] = true
		adj[j][i] = true
	}
}

func bfs() int {
	for i := 0; i < N; i++ {
		visited[i] = false
	}
	head, tail, count := 0, 0, 0
	visited[0] = true
	queue[tail] = 0
	tail++
	for head < tail {
		cur := queue[head]
		head++
		count++
		for nb := 0; nb < N; nb++ {
			if adj[cur][nb] && !visited[nb] {
				visited[nb] = true
				queue[tail] = nb
				tail++
			}
		}
	}
	return count
}

func main() {
	setup()

	fmt.Println("ready")

	scanner := bufio.NewScanner(os.Stdin)
	for scanner.Scan() {
		fmt.Println(bfs())
	}
}
