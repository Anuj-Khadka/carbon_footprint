package main

import "fmt"

const V = 1000

func bfs(adj *[V][V]bool, start int) int {
	if start < 0 || start >= V {
		return 0
	}

	var visited [V]bool
	var queue [V]int
	head, tail := 0, 0
	count := 0

	visited[start] = true
	queue[tail] = start
	tail++

	for head < tail {
		cur := queue[head]
		head++
		count++
		for nb := 0; nb < V; nb++ {
			if adj[cur][nb] && !visited[nb] {
				visited[nb] = true
				if tail < V {
					queue[tail] = nb
					tail++
				}
			}
		}
	}

	return count
}

func main() {
	var adj [V][V]bool
	for i := 0; i < V-1; i++ {
		adj[i][i+1] = true
		adj[i+1][i] = true
	}
	for i := 0; i < V; i += 10 {
		j := (i*7 + 3) % V
		adj[i][j] = true
		adj[j][i] = true
	}

	fmt.Println(bfs(&adj, 0))
}
