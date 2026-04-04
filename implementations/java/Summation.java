public class Summation {
    static final int SMALL  = 100;
    static final int MEDIUM = 10000;
    static final int LARGE  = 1000000;

    static long summation(long[] arr, int n) {
        long sum = 0;
        for (int i = 0; i < n; i++) sum += arr[i];
        return sum;
    }

    public static void main(String[] args) {
        int n;
        switch (args[0]) {
            case "small":  n = SMALL;  break;
            case "medium": n = MEDIUM; break;
            case "large":  n = LARGE;  break;
            default: System.err.println("Unknown size: " + args[0]); return;
        }
        long[] arr = new long[n];
        for (int i = 0; i < n; i++) arr[i] = i + 1;
        System.out.println(summation(arr, n));
    }
}
