public class MatrixMultiplication {
    static final int SMALL  = 50;
    static final int MEDIUM = 200;
    static final int LARGE  = 500;

    public static void main(String[] args) {
        int n;
        switch (args[0]) {
            case "small":  n = SMALL;  break;
            case "medium": n = MEDIUM; break;
            case "large":  n = LARGE;  break;
            default: System.err.println("Unknown size: " + args[0]); return;
        }
        long[][] a = new long[n][n];
        long[][] b = new long[n][n];
        long[][] c = new long[n][n];
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                a[i][j] = i + j;
                b[i][j] = i - j;
            }
        }
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                long acc = 0;
                for (int k = 0; k < n; k++) acc += a[i][k] * b[k][j];
                c[i][j] = acc;
            }
        }
        System.out.println(c[n / 2][n / 2]);
    }
}
