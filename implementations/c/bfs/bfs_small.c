#include <stdio.h>
#include <string.h>
#include <stdbool.h>

#define SMALL   100
#define MEDIUM  1000
#define LARGE   5000
#define V_MAX   LARGE

static bool adj[V_MAX][V_MAX];
static bool visited[V_MAX];
static int  queue[V_MAX];

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

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: bfs <small|medium|large>\n");
        return 1;
    }

    int v;
    if      (strcmp(argv[1], "small")  == 0) v = SMALL;
    else if (strcmp(argv[1], "medium") == 0) v = MEDIUM;
    else if (strcmp(argv[1], "large")  == 0) v = LARGE;
    else {
        fprintf(stderr, "Unknown size: %s\n", argv[1]);
        return 1;
    }

    build_graph(v);
    printf("%d\n", bfs(0, v));
    return 0;
}
