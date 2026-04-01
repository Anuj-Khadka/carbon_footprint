public class BinarySearch {
    static int binarySearch(long[] arr, long target) {
        int lo = 0, hi = arr.length - 1;
        while (lo <= hi) {
            int mid = lo + (hi - lo) / 2;
            if      (arr[mid] == target) return mid;
            else if (arr[mid] <  target) lo = mid + 1;
            else                         hi = mid - 1;
        }
        return -1;
    }

    public static void main(String[] args) {
        int N = 1_000_000;
        long[] arr = new long[N];
        for (int i = 0; i < N; i++) arr[i] = (long) i * 2;
        long target = (long)(N - 1) * 2;
        int result = binarySearch(arr, target);
        System.out.println(result);
    }
}
