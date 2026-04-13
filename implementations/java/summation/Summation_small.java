import java.io.*;

public class Summation_Small {
    static final int N = 100;
    static long[] arr = new long[N];

    static void setup() {
        for (int i = 0; i < N; i++) {
            arr[i] = (long)(i + 1);
        }
    }

    static long summation() {
        long sum = 0;
        for (int i = 0; i < N; i++) {
            sum += arr[i];
        }
        return sum;
    }

    public static void main(String[] args) throws IOException {
        setup();

        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        System.out.println("ready");
        System.out.flush();

        String line;
        while ((line = br.readLine()) != null) {
            System.out.println(summation());
            System.out.flush();
        }
    }
}