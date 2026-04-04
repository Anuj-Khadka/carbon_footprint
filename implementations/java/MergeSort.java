public class MergeSort {
    static final int SMALL  = 100;
    static final int MEDIUM = 10000;
    static final int LARGE  = 1000000;

    static void merge(long[] arr, long[] temp, int left, int mid, int right) {
        for (int i = left; i <= right; i++) temp[i] = arr[i];
        int i = left, j = mid + 1, k = left;
        while (i <= mid && j <= right)
            arr[k++] = (temp[i] <= temp[j]) ? temp[i++] : temp[j++];
        while (i <= mid) arr[k++] = temp[i++];
        while (j <= right) arr[k++] = temp[j++];
    }

    static void mergeSortImpl(long[] arr, long[] temp, int left, int right) {
        if (left >= right) return;
        int mid = left + (right - left) / 2;
        mergeSortImpl(arr, temp, left, mid);
        mergeSortImpl(arr, temp, mid + 1, right);
        merge(arr, temp, left, mid, right);
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
        for (int i = 0; i < n; i++) arr[i] = n - i;
        long[] temp = new long[n];
        if (n > 1) mergeSortImpl(arr, temp, 0, n - 1);
        System.out.println(arr[n - 1]);
    }
}
