public class MatrixMultiplication {
    static final int N = 300;

    static long[][] a = new long[N][N];
    static long[][] b = new long[N][N];
    static long[][] c = new long[N][N];

    static void matrixMultiply() {
        for (int i = 0; i < N; i++) {
            for (int j = 0; j < N; j++) {
                long acc = 0;
                for (int k = 0; k < N; k++) {
                    acc += a[i][k] * b[k][j];
                }
                c[i][j] = acc;
            }
        }
    }

    public static void main(String[] args) {
        for (int i = 0; i < N; i++) {
            for (int j = 0; j < N; j++) {
                a[i][j] = i + j;
                b[i][j] = i - j;
            }
        }

        matrixMultiply();

        System.out.println(c[N / 2][N / 2]);
    }
}
