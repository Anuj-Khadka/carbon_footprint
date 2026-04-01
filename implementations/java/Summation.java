public class Summation {
    static final int N = 10_000_000;

    static long summation(long[] arr, int n) {
        long sum = 0;
        for (int i = 0; i < n; i++) {
            sum += arr[i];
        }
        return sum;
    }

    public static void main(String[] args) {
        long[] arr = new long[N];
        for (int i = 0; i < N; i++) {
            arr[i] = i + 1;
        }
        System.out.println(summation(arr, N));
    }
}
