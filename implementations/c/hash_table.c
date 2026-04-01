#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

#define TABLE_SIZE 10007
#define N          100000

typedef struct Node {
    int64_t key, value;
    struct Node *next;
} Node;

static Node *table[TABLE_SIZE];

static int hash(int64_t key) {
    return (int)((uint64_t)(key * 2654435761LL) % TABLE_SIZE);
}

static void insert(int64_t key, int64_t value) {
    int idx = hash(key);
    for (Node *n = table[idx]; n; n = n->next)
        if (n->key == key) { n->value = value; return; }
    Node *n = malloc(sizeof(Node));
    n->key = key; n->value = value;
    n->next = table[idx]; table[idx] = n;
}

static void delete(int64_t key) {
    int idx = hash(key);
    Node *n = table[idx], *prev = NULL;
    while (n) {
        if (n->key == key) {
            if (prev) prev->next = n->next;
            else      table[idx] = n->next;
            free(n); return;
        }
        prev = n; n = n->next;
    }
}

int main(void) {
    for (int i = 0; i < N; i++) insert(i, i * 2);
    for (int i = 0; i < N; i += 3) delete(i);
    int count = 0;
    for (int i = 0; i < TABLE_SIZE; i++)
        for (Node *n = table[i]; n; n = n->next) count++;
    printf("%d\n", count);
    return 0;
}




// new hash-table:
/* Open-addressing hash table with linear probing */
/*
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define TABLE_SIZE 1000
#define NUM_KEYS   750   

static int64_t keys[TABLE_SIZE];
static int64_t vals[TABLE_SIZE];
static bool    occupied[TABLE_SIZE];

static void table_init(void) {
    memset(occupied, false, sizeof(occupied));
}

static int hash(int64_t key) {
    return (int) (((uint64_t)key * 2654435761ULL) >> 20) % TABLE_SIZE;
}

static void insert(int64_t key, int64_t val) {
    int i = hash(key);
    while (occupied[i]) {
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
    return -1; // not found 
}

int main(void) {
    table_init();

    // Insert NUM_KEYS deterministic key-value pairs 
    for (int i = 0; i < NUM_KEYS; i++) {
        insert((int64_t)i * 7 + 3, (int64_t)i * 13 + 5);
    }

    // Lookup all inserted keys and accumulate checksum
    int64_t checksum = 0;
    for (int i = 0; i < NUM_KEYS; i++) {
        checksum += lookup((int64_t)i * 7 + 3);
    }

    printf("%lld\n", (long long)checksum);
    return 0;
}

*/