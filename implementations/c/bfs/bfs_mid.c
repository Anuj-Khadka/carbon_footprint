#include <stdio.h>
#include <string.h>
#include <stdbool.h>

#define N 1000

static bool adj[N][N];
static bool visited[N];
static int  queue[N];

static void setup(void) {
    memset(adj, false, sizeof(adj));
    for (int i = 0; i < N - 1; i++) {
        adj[i][i + 1] = true;
        adj[i + 1][i] = true;
    }
    for (int i = 0; i < N; i += 10) {
        int j = (i * 7 + 3) % N;
        adj[i][j] = true;
        adj[j][i] = true;
    }
}

static int bfs(void) {
    memset(visited, false, sizeof(visited));
    int head = 0, tail = 0, count = 0;

    visited[0] = true;
    queue[tail++] = 0;

    while (head < tail) {
        int cur = queue[head++];
        count++;
        for (int nb = 0; nb < N; nb++) {
            if (adj[cur][nb] && !visited[nb]) {
                visited[nb]   = true;
                queue[tail++] = nb;
            }
        }
    }
    return count;
}

int main(void) {
    setup();

    printf("ready\n");
    fflush(stdout);

    char buf[64];
    while (fgets(buf, sizeof(buf), stdin)) {
        printf("%d\n", bfs());
        fflush(stdout);
    }

    return 0;
}