package merge_sort;

import java.io.*;

public class MergeSort_Large {
    static final int N = 1000000;
    static long[] arr  = new long[N];
    static long[] temp = new long[N];

    static void setup() {
        // reset handles initialization
    }

    static void reset() {
        for (int i = 0; i < N; i++) {
            arr[i] = (long)(N - i);
        }
    }

    static void merge(int left, int mid, int right) {
        for (int i = left; i <= right; i++) {
            temp[i] = arr[i];
        }
        int i = left, j = mid + 1, k = left;
        while (i <= mid && j <= right) {
            arr[k++] = (temp[i] <= temp[j]) ? temp[i++] : temp[j++];
        }
        while (i <= mid)   arr[k++] = temp[i++];
        while (j <= right) arr[k++] = temp[j++];
    }

    static void mergeSortImpl(int left, int right) {
        if (left >= right) return;
        int mid = left + (right - left) / 2;
        mergeSortImpl(left, mid);
        mergeSortImpl(mid + 1, right);
        merge(left, mid, right);
    }

    static long mergeSort() {
        reset();
        mergeSortImpl(0, N - 1);
        return arr[N - 1];
    }

    public static void main(String[] args) throws IOException {
        setup();

        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        System.out.println("ready");
        System.out.flush();

        String line;
        while ((line = br.readLine()) != null) {
            System.out.println(mergeSort());
            System.out.flush();
        }
    }
}