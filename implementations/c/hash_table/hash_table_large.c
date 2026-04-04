#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <inttypes.h>

#define N           100000
#define TABLE_SIZE  150001

static int64_t keys[TABLE_SIZE];
static int64_t vals[TABLE_SIZE];
static bool    occupied[TABLE_SIZE];

static int hash(int64_t key) {
    return (int)(((uint64_t)(key * 2654435761ULL)) % TABLE_SIZE);
}

static void insert(int64_t key, int64_t val) {
    int i = hash(key);
    while (occupied[i]) {
        if (keys[i] == key) { vals[i] = val; return; }
        i = (i + 1) % TABLE_SIZE;
    }
    keys[i]     = key;
    vals[i]     = val;
    occupied[i] = true;
}

static int64_t lookup(int64_t key) {
    int i = hash(key);
    while (occupied[i]) {
        if (keys[i] == key) return vals[i];
        i = (i + 1) % TABLE_SIZE;
    }
    return -1;
}

static void reset(void) {
    for (int i = 0; i < TABLE_SIZE; i++) {
        occupied[i] = false;
    }
    for (int i = 0; i < N; i++) {
        insert((int64_t)i * 7 + 3, (int64_t)i * 13 + 5);
    }
}

static int64_t hash_table(void) {
    reset();
    int64_t checksum = 0;
    for (int i = 0; i < N; i++) {
        checksum += lookup((int64_t)i * 7 + 3);
    }
    return checksum;
}

int main(void) {
    printf("ready\n");
    fflush(stdout);

    char buf[64];
    while (fgets(buf, sizeof(buf), stdin)) {
        printf("%" PRId64 "\n", hash_table());
        fflush(stdout);
    }

    return 0;
}