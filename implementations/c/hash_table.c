#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <inttypes.h>

#define SMALL       100
#define MEDIUM      10000
#define LARGE       100000
#define TABLE_SIZE  150001

static int64_t keys[TABLE_SIZE];
static int64_t vals[TABLE_SIZE];
static bool    occupied[TABLE_SIZE];

static void table_clear(void) {
    memset(occupied, false, sizeof(occupied));
}

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

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: hash_table <small|medium|large>\n");
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

    table_clear();
    for (int i = 0; i < n; i++) {
        insert((int64_t)i * 7 + 3, (int64_t)i * 13 + 5);
    }

    int64_t checksum = 0;
    for (int i = 0; i < n; i++) {
        checksum += lookup((int64_t)i * 7 + 3);
    }

    printf("%" PRId64 "\n", checksum);
    return 0;
}
