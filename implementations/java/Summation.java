public class Summation {
    static long summation(long[] arr) {
        long sum = 0;
        for (long x : arr) sum += x;
        return sum;
    }

    public static void main(String[] args) {
        int N = 10_000_000;
        long[] arr = new long[N];
        for (int i = 0; i < N; i++) arr[i] = i + 1;
        System.out.println(summation(arr));
    }
}
