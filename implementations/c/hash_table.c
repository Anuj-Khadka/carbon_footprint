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
