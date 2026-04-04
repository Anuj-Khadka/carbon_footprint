public class BinarySearch {
    static final int SMALL  = 100;
    static final int MEDIUM = 10000;
    static final int LARGE  = 1000000;

    static int binarySearch(long[] arr, int n, long target) {
        int lo = 0, hi = n - 1;
        while (lo <= hi) {
            int mid = lo + (hi - lo) / 2;
            if (arr[mid] == target) return mid;
            else if (arr[mid] < target) lo = mid + 1;
            else hi = mid - 1;
        }
        return -1;
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
        for (int i = 0; i < n; i++) arr[i] = (long) i * 2;
        long target = (long)(n - 1) * 2;
        System.out.println(binarySearch(arr, n, target));
    }
}
