public class BFS {
    static final int SMALL  = 100;
    static final int MEDIUM = 1000;
    static final int LARGE  = 5000;

    static int bfs(boolean[][] adj, int start, int v) {
        boolean[] visited = new boolean[v];
        int[] queue = new int[v];
        int head = 0, tail = 0, count = 0;
        visited[start] = true;
        queue[tail++] = start;
        while (head < tail) {
            int cur = queue[head++];
            count++;
            for (int nb = 0; nb < v; nb++) {
                if (adj[cur][nb] && !visited[nb]) {
                    visited[nb] = true;
                    queue[tail++] = nb;
                }
            }
        }
        return count;
    }

    static boolean[][] buildGraph(int v) {
        boolean[][] adj = new boolean[v][v];
        for (int i = 0; i < v - 1; i++) {
            adj[i][i + 1] = true;
            adj[i + 1][i] = true;
        }
        for (int i = 0; i < v; i += 10) {
            int j = (i * 7 + 3) % v;
            adj[i][j] = true;
            adj[j][i] = true;
        }
        return adj;
    }

    public static void main(String[] args) {
        int v;
        switch (args[0]) {
            case "small":  v = SMALL;  break;
            case "medium": v = MEDIUM; break;
            case "large":  v = LARGE;  break;
            default: System.err.println("Unknown size: " + args[0]); return;
        }
        boolean[][] adj = buildGraph(v);
        System.out.println(bfs(adj, 0, v));
    }
}
