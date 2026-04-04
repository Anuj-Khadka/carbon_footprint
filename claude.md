# CLAUDE.md — Carbon Footprint Research Project

This file describes the research context, methodology, codebase structure, and coding conventions for this project. It is intended to orient Claude Code when assisting with code cleanup, refactoring, or new implementations.

---

## Project Overview

This is an undergraduate honors research project at Caldwell University. The research question is:

**Does programming language choice affect carbon footprint (measured in gCO2e) when running identical algorithms on identical hardware?**

The project aims to produce a journal-quality published paper.

---

## Hardware & Environment

- **Machine**: Intel Core i7-14700K (3.40 GHz), 32 GB RAM, Windows 11 Enterprise 25H2
- **Why this hardware**: Intel RAPL (Running Average Power Limit) support enables direct hardware-level energy measurement via LibreHardwareMonitor
- **Working directory**: `C:\Users\AKhadka2\Desktop\carbon_footprint`
- **Python environment**: `.venv` in the project root

### Installed Runtimes (all in System PATH)

| Language   | Runtime / Version            |
|------------|------------------------------|
| C          | GCC 14.3.0 (WinLibs, `C:\gcc\bin`) |
| Rust       | 1.94.0                       |
| Go         | 1.26.1                       |
| Java       | OpenJDK 21.0.10 (Temurin)    |
| JavaScript | Node.js v24.14.0             |
| Python     | 3.12.10                      |

> **Note**: All runtimes must be in **system PATH** (not user PATH) to be visible to Python subprocesses running as Administrator.

---

## Research Design

### Languages (6)

C, Rust, Go, Java, JavaScript, Python — chosen to represent six distinct paradigms:

| Language   | Paradigm                  |
|------------|---------------------------|
| C          | Manual memory management  |
| Rust       | Ownership-based memory    |
| Go         | Compiled with GC          |
| Java       | OOP / JVM                 |
| JavaScript | JIT / Dynamic             |
| Python     | Interpreted               |

### Algorithms (6)

Each algorithm is implemented in all 6 languages at 3 input sizes (small / medium / large):

1. `summation`
2. `binary_search`
3. `merge_sort`
4. `bfs` (Breadth-First Search)
5. `hash_table`
6. `matrix_multiplication` (Matrix Multiplication)

### Primary Metric

```
gCO2e = Energy (kWh) × Carbon Intensity (gCO2/kWh)
```

- **Energy**: Measured via Intel RAPL through LibreHardwareMonitor
- **Carbon intensity**: Fetched from [Electricity Maps API](https://www.electricitymaps.com/), zone `US-NY-NYIS`

---

## Core Design Decisions
 
These are **settled decisions** — do not refactor away from them without explicit instruction.
 
### 1. Static Globals, No Heap Allocation
 
All algorithm implementations use **static global arrays** with **hardcoded, deterministic input data**. There is no dynamic memory allocation (no `malloc`, no `new`, no heap vectors), no file I/O, and no random data generation.
 
**Why**: Eliminates memory allocation overhead and I/O variability from energy measurements, so the only variable is language runtime behavior.
 
### 2. C as Reference Baseline
 
C is the reference implementation. All other languages must produce **byte-identical stdout output** to the C version for each algorithm and input size. Correctness is verified by `verify_outputs.py`.
 
### 3. Simplicity First
 
The guiding principle for all implementations and scripts is **minimal viable complexity**. Avoid unnecessary abstractions, error handling, or features that peer reviewers would need to trace through. If something can be done simply, it should be.
 
### 4. No pyRAPL
 
pyRAPL is Linux-only (reads from `/sys/devices/system/cpu/present`) and does not work on Windows. The correct Windows-native RAPL tool is **LibreHardwareMonitor**, accessed via its kernel driver service.
 
---

## Directory Structure

```
carbon_footprint/
    ├── venv/                    # Python virtual environment
    ├── docs/
    ├── paper/
    ├── implementations/
        ├── c/                        # C implementations
        │   ├── summation.c
        │   ├── binary_search.c
        │   ├── merge_sort.c
        │   ├── bfs.c
        │   ├── hash_table.c
        │   └── matrix_mul.c
        ├── rust/                     # Rust implementations
        ├── go/                       # Go implementations
        ├── java/                     # Java implementations
        ├── js/                       # JavaScript implementations
        ├── python/                   # Python implementations
    ├── verify_runtimes.py        # Confirms all 6 runtimes are accessible
    ├── verify_outputs.py         # Compiles & runs each language, compares stdout to C reference
    ├── test_harness.py           # Main experiment runner (RAPL + Electricity Maps + logging)
    ├── results/                  # Experiment output (JSONL logs, CSV/JSON reports)
    └── CLAUDE.md                 # This file
```

---
## Algorithm Implementations
 
Each implementation must:
 
1. Use **static/global arrays** for all data (no heap allocation)
2. Use **hardcoded, deterministic input** (same values across all languages)
3. Print results to **stdout** in the exact same format as the C reference
4. Have **no file I/O**, **no command-line argument parsing** (input sizes are compile-time or hard-coded constants)
5. Be as **structurally identical** to the C version as the language allows
 
### Input Sizes
 
Each algorithm runs at three sizes. The sizes are defined as constants in each file:
 
| Size   | Meaning (algorithm-dependent)     |
|--------|-----------------------------------|
| small  | e.g., N=100 or array of 100 ints  |
| medium | e.g., N=10,000                    |
| large  | e.g., N=1,000,000                 |
 
### Sequential Execution Within One Run
 
Each language's program runs **all three input sizes in a single execution** — `main()` (or equivalent) calls the algorithm at small, then medium, then large size sequentially and prints results for each. There is no separate binary/invocation per size. This mirrors the C reference design exactly.
 
---


## Compilation & Execution Commands
 
These are the exact commands used by `verify_outputs.py` and `test_harness.py` to build and run each language. Do not change these without updating both scripts.
 
| Language   | Compile                                              | Run                          |
|------------|------------------------------------------------------|------------------------------|
| C          | `gcc -O2 -o <out> <file>.c`                          | `./<out>`                    |
| Rust       | `rustc -O -o <out> <file>.rs`                        | `./<out>`                    |
| Go         | `go build -o <out> <file>.go`                        | `./<out>`                    |
| Java       | `javac <file>.java`                                  | `java <ClassName>`           |
| JavaScript | *(no compile step)*                                  | `node <file>.js`             |
| Python     | *(no compile step)*                                  | `python <file>.py`           |
 
> All compilation uses optimization flags (`-O2` / `-O`) to reflect realistic production-like performance. Java uses default `javac` with no special flags.
 
---

## Key Scripts

### `verify_runtimes.py`
 
Checks that all 6 runtimes are on PATH and executable. Prints PASS/FAIL per language.
 
### `verify_outputs.py`
 
- Compiles and runs each language's implementation of each algorithm
- Compares stdout line-by-line against the C reference output
- Prints **PASS or FAIL** per (language, algorithm) pair to terminal — there is no SKIP state; compile/runtime failures count as FAIL
- Writes a JSON report summarizing results
 
### `test_harness.py`
 
The main experiment runner. Responsibilities:
- Reads RAPL energy data via LibreHardwareMonitor (Windows kernel driver)
- Fetches live carbon intensity from Electricity Maps API (zone: `US-NY-NYIS`)
- Runs each (language × algorithm × input_size) combination for N repetitions
- Logs each run to a JSONL file
- Produces CSV and JSON summary reports
- Supports CLI flags for filtering by language or algorithm
 
> Keep this script focused and simple. Avoid adding features unless explicitly requested.

### JSONL Log Schema
 
Each run is appended as one JSON object per line to the results log. Fields:
 
```json
{
  "language": "python",
  "algorithm": "merge_sort",
  "input_size": "large",
  "run_index": 3,
  "energy_j": 0.452,
  "energy_kwh": 1.256e-7,
  "carbon_intensity_gco2_kwh": 214.3,
  "gco2e": 2.69e-5,
  "duration_s": 1.834,
  "timestamp": "2026-01-15T22:14:03"
}
```

Do not rename or remove fields — downstream analysis scripts depend on this schema.

---

## Energy Measurement: LibreHardwareMonitor
 
- LibreHardwareMonitor must be running as a Windows service with its kernel driver loaded
- Driver is registered via elevated Command Prompt:
  ```
  sc create LibreHardwareMonitor binPath= "C:\path\to\LibreHardwareMonitor.exe" start= auto
  sc start LibreHardwareMonitor
  ```
- Python connects to its local web server (default: `http://localhost:8085`) to read RAPL sensor values
- The relevant sensor path is the CPU Package energy sensor
 
---

## Carbon Intensity: Electricity Maps API

- Zone: `US-NY-NYIS` (New York)
- API key stored in environment variable or `.env` file (never hardcoded)
- Fetched once per experiment batch, not once per run
- Units: gCO2/kWh

---

## Carbon Intensity: Electricity Maps API
 
- Zone: `US-NY-NYIS` (New York)
- API key stored in environment variable or `.env` file (never hardcoded)
- Fetched once per **language-algorithm pair** (not once per individual run, not once per full session)
- Units: gCO2/kWh
 
---
 
## Statistical Methodology
 
### Pilot Study
 
Before the main experiment, a pilot study is run to measure variance and determine the required sample size. It runs **50 repetitions** per (language × algorithm) pair and produces:
 
- **Terminal output**: Live progress and per-pair variance summary printed to console
- **CSV**: Raw per-run energy readings for every (language, algorithm, run_index)
- **JSON**: Variance summary per (language, algorithm) pair
- **Recommended N**: Power analysis result printed to terminal — the minimum sample size needed for the main experiment to achieve the target power
 
The recommended N from the pilot study drives the main experiment's repetition count.
 
### Sample Size (Main Experiment)
 
Determined by pilot study power analysis targeting:
- Power = 0.80
- α = 0.05 (Bonferroni-corrected across 15 pairwise language comparisons)
 
### Tests
 
| Test | Purpose |
|------|---------|
| Welch's t-test | Pairwise comparisons (does not assume equal variance) | This is the primary test we will do for this research. |
| Bonferroni correction | Controls family-wise error rate across 15 pairs | This will be done later. |
| Shapiro-Wilk | Normality testing per (language, algorithm) group | We will skip this for now. |
 
### Experiment Timing
 
Main experiment runs are scheduled for **off-peak hours (10 PM – 6 AM)** to minimize carbon intensity variance and system load interference.
 
---
 
## Coding Conventions
 
- **Python scripts**: PEP 8, type hints optional but welcome, docstrings on functions
- **C**: K&R style, static globals declared at file top, `main()` runs all three sizes sequentially and prints results
- **All languages**: Match the C output format exactly — same number of lines, same numeric precision, same labels
- **No magic numbers**: Define input sizes as named constants at the top of each file
- **No unnecessary comments**: Code should be self-explanatory; add comments only where non-obvious
 
---
 
## What "Cleanup" Means for This Codebase
 
When refactoring or cleaning up, Claude Code should:
 
1. **Preserve all static globals and hardcoded data** — do not replace with dynamic allocation or file reads
2. **Preserve stdout format exactly** — any change to print statements must be verified against C reference
3. **Keep scripts simple** — remove dead code, redundant logic, or over-engineered abstractions
4. **Ensure consistent input sizes** — all languages must use the same small/medium/large values
5. **Do not add features** — cleanup means tidy, not expand
6. **Flag any output format discrepancies** — if a language's output doesn't match C, report it rather than silently fixing it
 
---
