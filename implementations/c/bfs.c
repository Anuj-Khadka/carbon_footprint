#include <stdio.h>
#include <string.h>
#include <stdbool.h>

#define V 1000  

static bool adj[V][V];
static bool visited[V];
static int  queue[V];

static int bfs(int start) {
    if (start < 0 || start >= V) {
        return 0;
    }

    memset(visited, false, sizeof(visited));
    int head = 0, tail = 0, count = 0;

    visited[start] = true;
    queue[tail++]  = start;

    while (head < tail) {
        int cur = queue[head++];
        count++;


        for (int nb = 0; nb < V; nb++) {
            if (adj[cur][nb] && !visited[nb]) {
                visited[nb]   = true;
                if (tail < V) {
                    queue[tail++] = nb;
                }
            }
        }
    }


    return count;
}

int main(void) {

    for (int i = 0; i < V - 1; i++) {
        adj[i][i + 1] = true;
        adj[i + 1][i] = true;
    }
    for (int i = 0; i < V; i += 10) {
        int j = (i * 7 + 3) % V;
        adj[i][j] = true;
        adj[j][i] = true;
    }

    printf("%d\n", bfs(0));
    return 0;
}