"""
verify_outputs.py
-----------------
Runs all 36 implementations and checks that every language
produces the same output as C (the reference baseline).

Pre-requisites (must compile first):
  C:    cd implementations/c    && bash compile.sh
  Java: cd implementations/java && javac *.java
  Rust: cd implementations/rust/<algo> && cargo build --release  (x6)

Usage:
  python verification/verify_outputs.py
"""

import subprocess
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMPL = os.path.join(ROOT, "implementations")

ALGORITHMS = [
    "summation",
    "binary_search",
    "merge_sort",
    "bfs",
    "hash_table",
    "matrix_multiplication",
]

JAVA_CLASS = {
    "summation":             "Summation",
    "binary_search":         "BinarySearch",
    "merge_sort":            "MergeSort",
    "bfs":                   "BFS",
    "hash_table":            "HashTable",
    "matrix_multiplication": "MatrixMultiplication",
}

RUNNERS = {
    "C":          lambda a: [f"{IMPL}/c/bin/{a}.exe"],
    "Python":     lambda a: ["python", f"{IMPL}/python/{a}.py"],
    "JavaScript": lambda a: ["node", f"{IMPL}/javascript/{a}.js"],
    "Java":       lambda a: ["java", "-cp", f"{IMPL}/java", JAVA_CLASS[a]],
    "Go":         lambda a: ["go", "run", f"{IMPL}/go/{a}.go"],
    "Rust":       lambda a: [f"{IMPL}/rust/{a}/target/release/{a}.exe"],
}


def run(cmd, timeout=300):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip() or f"ERROR: {r.stderr.strip()}"
    except FileNotFoundError:
        return "ERROR: not found (not compiled?)"
    except subprocess.TimeoutExpired:
        return f"ERROR: timeout after {timeout}s"


def normalize(s):
    # Round floats to 2 dp so languages don't differ on precision
    try:
        return f"{float(s):.2f}"
    except (ValueError, TypeError):
        return s


passes = fails = 0

print("=" * 50)
print("  Output Verification  —  baseline: C")
print("=" * 50)

for algo in ALGORITHMS:
    print(f"\n{algo.replace('_', ' ').upper()}")

    ref = normalize(run(RUNNERS["C"](algo)))
    print(f"  {'C':<14} {ref}  (ref)")

    for lang, cmd_fn in list(RUNNERS.items())[1:]:
        out    = normalize(run(cmd_fn(algo)))
        passed = out == ref and not out.startswith("ERROR")
        status = "PASS" if passed else "FAIL"
        note   = "" if passed else f"  ← expected {ref}"
        print(f"  {status}  {lang:<12} {out}{note}")
        if passed: passes += 1
        else:      fails  += 1

print(f"\n{'=' * 50}")
print(f"  {passes} passed, {fails} failed out of {passes + fails}")
print("=" * 50)
