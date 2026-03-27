# Carbon Footprint of Programming Languages

## Research question
When running the same algorithms on the same hardware, how much 
does the programming language alone affect carbon footprint emission?

## Researcher
Anuj Khadka — akhadka2@caldwell.edu  
Caldwell University, Spring 2026

## Advisor
Prof. Vlad Veksler — vveksler@caldwell.edu

## Languages studied
C, Rust, Go, Java, JavaScript, Python

## Algorithms studied
Summation, Binary Search, Merge Sort, BFS, Hash Table, 
Matrix Multiplication

## Hardware
Intel Core i7-14700K · 32GB RAM · Windows 11

## How to reproduce
1. See environment.md for exact runtime versions
2. Install Python dependencies: pip install -r requirements.txt
3. Run verify_runtimes.py to confirm environment
4. See docs/pre_run_protocol.md before running experiments

## Repository structure
- implementations/ — all algorithm implementations
- experiments/     — test harness and raw data
- analysis/        — statistical analysis scripts
- paper/           — LaTeX source for journal paper
- docs/            — protocols and research decisions log

#### Summation
- creates an array of 1million elements and adds them up.

### Merge Sort
- creates an array of 1 to 1million in reverse order and sorts it.  * - Uses one auxiliary buffer allocated once instead of per-merge allocations. no malloc/free on every merge call.
- Allocation happens once, so less allocator overhead and less measurement noise.
- Time is still O(n log n), extra memory is O(n), but with cleaner runtime behavior.


### Binary Search
- using reps to loop reps times and store the final result. reduces noice. larger energy dataset. if not thing, returns -1 (but willnot lol)


### Matrix
- use basic formula, no algorithms.
```

A = 
[ 0  1  2  3 ]
[ 1  2  3  4 ]
[ 2  3  4  5 ]
[ 3  4  5  6 ]

B = 
[  0  -1  -2  -3 ]
[  1   0  -1  -2 ]
[  2   1   0  -1 ]
[  3   2   1   0 ]


C = Multiply...

but this happens for 300*300

```

























































Runtime vs n
Carbon vs n

then analyze:
- how fast emissions grow
- which language scales better