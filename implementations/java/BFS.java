import java.util.ArrayDeque;

public class BFS {
    static int bfs(int[][] adj, int V, int start) {
        boolean[] visited = new boolean[V];
        ArrayDeque<Integer> queue = new ArrayDeque<>();
        visited[start] = true;
        queue.add(start);
        int count = 0;
        while (!queue.isEmpty()) {
            int cur = queue.poll();
            count++;
            for (int nb : adj[cur]) {
                if (!visited[nb]) { visited[nb] = true; queue.add(nb); }
            }
        }
        return count;
    }

    public static void main(String[] args) {
        int V = 10_000;
        int[][] adj = new int[V][2];
        for (int i = 0; i < V; i++) {
            adj[i][0] = (i + 1) % V;
            adj[i][1] = (i * 7 + 3) % V;
        }
        System.out.println(bfs(adj, V, 0));
    }
}
