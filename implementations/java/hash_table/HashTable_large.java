package hash_table;

import java.io.*;

public class HashTable_Large {
    static final int N          = 100000;
    static final int TABLE_SIZE = 150001;

    static long[]    keys     = new long[TABLE_SIZE];
    static long[]    vals     = new long[TABLE_SIZE];
    static boolean[] occupied = new boolean[TABLE_SIZE];

    static void setup() {
        // reset handles initialization
    }

    static int hashFn(long key) {
        return (int)(((key * 2654435761L) & 0xFFFFFFFFFFFFFFFFL) % TABLE_SIZE);
    }

    static void insert(long key, long val) {
        int i = hashFn(key);
        while (occupied[i]) {
            if (keys[i] == key) { vals[i] = val; return; }
            i = (i + 1) % TABLE_SIZE;
        }
        keys[i]     = key;
        vals[i]     = val;
        occupied[i] = true;
    }

    static long lookup(long key) {
        int i = hashFn(key);
        while (occupied[i]) {
            if (keys[i] == key) return vals[i];
            i = (i + 1) % TABLE_SIZE;
        }
        return -1;
    }

    static void reset() {
        for (int i = 0; i < TABLE_SIZE; i++) occupied[i] = false;
        for (int i = 0; i < N; i++) insert((long)i * 7 + 3, (long)i * 13 + 5);
    }

    static long hashTable() {
        reset();
        long checksum = 0;
        for (int i = 0; i < N; i++) checksum += lookup((long)i * 7 + 3);
        return checksum;
    }

    public static void main(String[] args) throws IOException {
        setup();

        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        System.out.println("ready");
        System.out.flush();

        String line;
        while ((line = br.readLine()) != null) {
            System.out.println(hashTable());
            System.out.flush();
        }
    }
}