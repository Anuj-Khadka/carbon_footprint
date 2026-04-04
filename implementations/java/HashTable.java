public class HashTable {
    static final int SMALL      = 100;
    static final int MEDIUM     = 10000;
    static final int LARGE      = 100000;
    static final int TABLE_SIZE = 150001;

    static long[] keys     = new long[TABLE_SIZE];
    static long[] vals     = new long[TABLE_SIZE];
    static boolean[] occupied = new boolean[TABLE_SIZE];

    static void tableClear() {
        java.util.Arrays.fill(occupied, false);
    }

    static int hash(long key) {
        return (int)(((key * 2654435761L) & 0xFFFFFFFFFFFFFFFFL) % TABLE_SIZE);
    }

    static void insert(long key, long val) {
        int i = hash(key);
        while (occupied[i]) {
            if (keys[i] == key) { vals[i] = val; return; }
            i = (i + 1) % TABLE_SIZE;
        }
        keys[i] = key;
        vals[i] = val;
        occupied[i] = true;
    }

    static long lookup(long key) {
        int i = hash(key);
        while (occupied[i]) {
            if (keys[i] == key) return vals[i];
            i = (i + 1) % TABLE_SIZE;
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
        tableClear();
        for (int i = 0; i < n; i++) insert((long)i * 7 + 3, (long)i * 13 + 5);
        long checksum = 0;
        for (int i = 0; i < n; i++) checksum += lookup((long)i * 7 + 3);
        System.out.println(checksum);
    }
}
