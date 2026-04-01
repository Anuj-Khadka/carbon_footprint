public class BFS {
    static final int V = 1000;

    static int bfs(boolean[][] adj, int start) {
        if (start < 0 || start >= V) {
            return 0;
        }

        boolean[] visited = new boolean[V];
        int[] queue = new int[V];
        int head = 0;
        int tail = 0;
        int count = 0;

        visited[start] = true;
        queue[tail++] = start;

        while (head < tail) {
            int cur = queue[head++];
            count++;

            for (int nb = 0; nb < V; nb++) {
                if (adj[cur][nb] && !visited[nb]) {
                    visited[nb] = true;
                    if (tail < V) {
                        queue[tail++] = nb;
                    }
                }
            }
        }

        return count;
    }

    public static void main(String[] args) {
        boolean[][] adj = new boolean[V][V];

        for (int i = 0; i < V - 1; i++) {
            adj[i][i + 1] = true;
            adj[i + 1][i] = true;
        }
        for (int i = 0; i < V; i += 10) {
            int j = (i * 7 + 3) % V;
            adj[i][j] = true;
            adj[j][i] = true;
        }

        System.out.println(bfs(adj, 0));
    }
}
