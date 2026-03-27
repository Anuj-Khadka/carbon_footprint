public class MergeSort {
    static void merge(long[] arr, int l, int m, int r) {
        int ln = m - l + 1, rn = r - m;
        long[] L = new long[ln], R = new long[rn];
        for (int i = 0; i < ln; i++) L[i] = arr[l + i];
        for (int j = 0; j < rn; j++) R[j] = arr[m + 1 + j];
        int i = 0, j = 0, k = l;
        while (i < ln && j < rn) arr[k++] = (L[i] <= R[j]) ? L[i++] : R[j++];
        while (i < ln) arr[k++] = L[i++];
        while (j < rn) arr[k++] = R[j++];
    }

    static void mergeSort(long[] arr, int l, int r) {
        if (l >= r) return;
        int m = l + (r - l) / 2;
        mergeSort(arr, l, m);
        mergeSort(arr, m + 1, r);
        merge(arr, l, m, r);
    }

    public static void main(String[] args) {
        int N = 1_000_000;
        long[] arr = new long[N];
        for (int i = 0; i < N; i++) arr[i] = N - i;
        mergeSort(arr, 0, N - 1);
        System.out.println(arr[N - 1]);
    }
}
