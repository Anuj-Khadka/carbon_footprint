```
import java.io.*;

public class Summation_Small {
    static final int N = 100;
    static long[] arr = new long[N];

    static void setup() { ... }
    static long algorithm() { ... }

    public static void main(String[] args) throws IOException {
        setup();

        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        System.out.println("ready");
        System.out.flush();

        String line;
        while ((line = br.readLine()) != null) {
            System.out.println(algorithm());
            System.out.flush();
        }
    }
}
```