#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

#define V 10000

static int adj[V][2];

static int bfs(int start) {
    bool *visited = calloc(V, sizeof(bool));
    int  *queue   = malloc(V * sizeof(int));
    int   head = 0, tail = 0, count = 0;
    visited[start] = true;
    queue[tail++]  = start;
    while (head < tail) {
        int cur = queue[head++];
        count++;
        for (int i = 0; i < 2; i++) {
            int nb = adj[cur][i];
            if (!visited[nb]) {
                visited[nb]   = true;
                queue[tail++] = nb;
            }
        }
    }
    free(visited);
    free(queue);
    return count;
}

int main(void) {
    for (int i = 0; i < V; i++) {
        adj[i][0] = (i + 1) % V;
        adj[i][1] = (i * 7 + 3) % V;
    }
    printf("%d\n", bfs(0));
    return 0;
}
