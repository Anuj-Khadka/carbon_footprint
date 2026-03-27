public class HashTable {
    static final int TABLE_SIZE = 10007;
    static final int N          = 100_000;

    static class Node {
        long key, value;
        Node next;
        Node(long k, long v, Node n) { key = k; value = v; next = n; }
    }

    static Node[] table = new Node[TABLE_SIZE];

    static int hash(long key) {
        return (int)(Math.abs(key * 2654435761L) % TABLE_SIZE);
    }

    static void insert(long key, long value) {
        int idx = hash(key);
        for (Node n = table[idx]; n != null; n = n.next)
            if (n.key == key) { n.value = value; return; }
        table[idx] = new Node(key, value, table[idx]);
    }

    static void delete(long key) {
        int idx = hash(key);
        Node n = table[idx], prev = null;
        while (n != null) {
            if (n.key == key) {
                if (prev != null) prev.next = n.next;
                else table[idx] = n.next;
                return;
            }
            prev = n; n = n.next;
        }
    }

    public static void main(String[] args) {
        for (int i = 0; i < N; i++) insert(i, i * 2);
        for (int i = 0; i < N; i += 3) delete(i);
        int count = 0;
        for (Node n : table) while (n != null) { count++; n = n.next; }
        System.out.println(count);
    }
}
