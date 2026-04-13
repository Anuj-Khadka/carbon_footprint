package binary_search;

import java.io.*;

public class BinarySearch_Mid {
    static final int N = 10000;
    static long[] arr = new long[N];

    static void setup() {
        for (int i = 0; i < N; i++) {
            arr[i] = (long)i * 2;
        }
    }

    static int binarySearch() {
        long target = (long)(N - 1) * 2;
        int lo = 0, hi = N - 1;
        while (lo <= hi) {
            int mid = lo + (hi - lo) / 2;
            if (arr[mid] == target)      return mid;
            else if (arr[mid] < target)  lo = mid + 1;
            else                         hi = mid - 1;
        }
        return -1;
    }

    public static void main(String[] args) throws IOException {
        setup();

        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        System.out.println("ready");
        System.out.flush();

        String line;
        while ((line = br.readLine()) != null) {
            System.out.println(binarySearch());
            System.out.flush();
        }
    }
}