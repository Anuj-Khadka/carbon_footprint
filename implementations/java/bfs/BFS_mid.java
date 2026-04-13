package bfs;

import java.io.*;

public class BFS_Mid {
    static final int N = 1000;
    static boolean[][] adj     = new boolean[N][N];
    static boolean[]   visited = new boolean[N];
    static int[]       queue   = new int[N];

    static void setup() {
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

    static int bfs() {
        for (int i = 0; i < N; i++) visited[i] = false;
        int head = 0, tail = 0, count = 0;
        visited[0]    = true;
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

    public static void main(String[] args) throws IOException {
        setup();

        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        System.out.println("ready");
        System.out.flush();

        String line;
        while ((line = br.readLine()) != null) {
            System.out.println(bfs());
            System.out.flush();
        }
    }
}