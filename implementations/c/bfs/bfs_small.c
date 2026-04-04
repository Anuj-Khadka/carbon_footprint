#include <stdio.h>
#include <string.h>
#include <stdbool.h>

#define SMALL  100
#define MEDIUM 1000
#define LARGE  5000

static bool adj[LARGE][LARGE];
static bool visited[LARGE];
static int  queue[LARGE];

static int bfs(int start, int v) {
    memset(visited, false, (size_t)v * sizeof(bool));
    int head = 0, tail = 0, count = 0;

    visited[start] = true;
    queue[tail++]  = start;

    while (head < tail) {
        int cur = queue[head++];
        count++;
        for (int nb = 0; nb < v; nb++) {
            if (adj[cur][nb] && !visited[nb]) {
                visited[nb]   = true;
                queue[tail++] = nb;
            }
        }
    }
    return count;
}

static void build_graph(int v) {
    memset(adj, false, sizeof(adj));
    for (int i = 0; i < v - 1; i++) {
        adj[i][i + 1] = true;
        adj[i + 1][i] = true;
    }
    for (int i = 0; i < v; i += 10) {
        int j = (i * 7 + 3) % v;
        adj[i][j] = true;
        adj[j][i] = true;
    }
}

int main(void) {
    build_graph(SMALL);
    printf("small:  %d\n", bfs(0, SMALL));

    build_graph(MEDIUM);
    printf("medium: %d\n", bfs(0, MEDIUM));

    build_graph(LARGE);
    printf("large:  %d\n", bfs(0, LARGE));

    return 0;
}