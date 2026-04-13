package matrix_multiplication;

import java.io.*;

public class MatrixMultiplication_Mid {
    static final int N = 200;
    static long[][] a = new long[N][N];
    static long[][] b = new long[N][N];
    static long[][] c = new long[N][N];

    static void setup() {
        for (int i = 0; i < N; i++) {
            for (int j = 0; j < N; j++) {
                a[i][j] = (long)i + j;
                b[i][j] = (long)i - j;
            }
        }
    }

    static long matrixMul() {
        for (int i = 0; i < N; i++) {
            for (int j = 0; j < N; j++) {
                long acc = 0;
                for (int k = 0; k < N; k++) {
                    acc += a[i][k] * b[k][j];
                }
                c[i][j] = acc;
            }
        }
        return c[N / 2][N / 2];
    }

    public static void main(String[] args) throws IOException {
        setup();

        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        System.out.println("ready");
        System.out.flush();

        String line;
        while ((line = br.readLine()) != null) {
            System.out.println(matrixMul());
            System.out.flush();
        }
    }
}