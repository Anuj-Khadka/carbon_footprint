input sizes - https://medium.com/%40anderson.meneses/understanding-sorting-algorithms-a-benchmarking-approach-with-b3r3ch1tsortingbenchmark-e810f7bc2c49

read this for benchmark justification - https://arxiv.org/pdf/1812.00661

not the thing is matrix multiplication uses the naive O(n³) algorithm without cache optimization, to isolate language overhead rather than algorithmic cleverness.




dfs over bfs because it is interesting for energy, the fifo pattern stresses the memory differently than a stack.




tried arguments but ut might not yet work, because need to run the file in each size and that startup costs.



```
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <inttypes.h>

#define SMALL   100
#define MEDIUM  10000
#define LARGE   1000000

static int64_t arr[LARGE];

static int64_t summation(int n) {
    int64_t sum = 0;
    for (int i = 0; i < n; i++) {
        sum += arr[i];
    }
    return sum;
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: summation <small|medium|large>\n");
        return 1;
    }

    int n;
    if      (strcmp(argv[1], "small")  == 0) n = SMALL;
    else if (strcmp(argv[1], "medium") == 0) n = MEDIUM;
    else if (strcmp(argv[1], "large")  == 0) n = LARGE;
    else {
        fprintf(stderr, "Unknown size: %s\n", argv[1]);
        return 1;
    }

    for (int i = 0; i < n; i++) {
        arr[i] = (int64_t)i + 1;
    }

    printf("%" PRId64 "\n", summation(n));
    return 0;
}

```

This is not a good approach. I am going to have a seperate file for each size. will explain this later.

new file:
```
setup() runs once before the loop — array fill is completely outside all measurements
printf("ready\n") tells the harness the program is initialized and waiting
fgets blocks until the harness sends a newline — that's the trigger
checksum prints immediately after the algorithm returns, then loops back to wait
fflush after every print is critical on Windows — without it stdout may buffer and the harness hangs waiting
```


using checksum for all this things. gives me a single output value. so that we can test the algo is running and producing right output.



set up is basically for setting the arr or whatever we are working with.



# for the merge sort the setup is intentionally empty because the reset happens per run