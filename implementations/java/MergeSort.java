public class MergeSort {
    static final int N = 1_000_000;
    static long[] temp = new long[N];

    static void mergeOnceBuffer(long[] arr, int left, int mid, int right) {
        for (int i = left; i <= right; i++) {
            temp[i] = arr[i];
        }

        int i = left, j = mid + 1, k = left;

        while (i <= mid && j <= right) {
            arr[k++] = (temp[i] <= temp[j]) ? temp[i++] : temp[j++];
        }

        while (i <= mid) {
            arr[k++] = temp[i++];
        }

        while (j <= right) {
            arr[k++] = temp[j++];
        }
    }

    static void mergeSortImpl(long[] arr, int left, int right) {
        if (left >= right) return;
        int mid = left + (right - left) / 2;
        mergeSortImpl(arr, left, mid);
        mergeSortImpl(arr, mid + 1, right);
        mergeOnceBuffer(arr, left, mid, right);
    }

    static void mergeSort(long[] arr, int n) {
        if (arr == null || n < 2) return;
        mergeSortImpl(arr, 0, n - 1);
    }

    public static void main(String[] args) {
        long[] arr = new long[N];
        for (int i = 0; i < N; i++) {
            arr[i] = N - i;
        }
        mergeSort(arr, N);
        System.out.println(arr[N - 1]);
    }
}
