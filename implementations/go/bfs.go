package main

import "fmt"

const V = 10_000

func bfs(adj [V][2]int, start int) int {
	var visited [V]bool
	queue := make([]int, 0, V)
	visited[start] = true
	queue = append(queue, start)
	count := 0
	for len(queue) > 0 {
		cur := queue[0]
		queue = queue[1:]
		count++
		for _, nb := range adj[cur] {
			if !visited[nb] {
				visited[nb] = true
				queue = append(queue, nb)
			}
		}
	}
	return count
}

func main() {
	var adj [V][2]int
	for i := 0; i < V; i++ {
		adj[i][0] = (i + 1) % V
		adj[i][1] = (i*7 + 3) % V
	}
	fmt.Println(bfs(adj, 0))
}
