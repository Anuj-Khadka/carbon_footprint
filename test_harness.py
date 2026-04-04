"""
test_harness.py
---------------
Compiles and runs algorithm implementations across languages.
Verifies output correctness against C reference values and reports timing.

Usage:
    python test_harness.py
"""

import subprocess
import os
import sys
import time

ROOT     = os.path.dirname(os.path.abspath(__file__))
IMPL_DIR = os.path.join(ROOT, "implementations")
BIN_DIR  = os.path.join(IMPL_DIR, "build")

ALGORITHMS = [
    "summation",
    "binary_search",
    "merge_sort",
    "bfs",
    "hash_table",
    "matrix_multiplication",
]

SIZES = ["small", "medium", "large"]

# C reference outputs — every language must match these
EXPECTED = {
    ("summation", "small"):               "5050",
    ("summation", "medium"):              "50005000",
    ("summation", "large"):               "500000500000",
    ("binary_search", "small"):           "99",
    ("binary_search", "medium"):          "9999",
    ("binary_search", "large"):           "999999",
    ("merge_sort", "small"):              "100",
    ("merge_sort", "medium"):             "10000",
    ("merge_sort", "large"):              "1000000",
    ("bfs", "small"):                     "100",
    ("bfs", "medium"):                    "1000",
    ("bfs", "large"):                     "5000",
    ("hash_table", "small"):              "64850",
    ("hash_table", "medium"):             "649985000",
    ("hash_table", "large"):              "64999850000",
    ("matrix_multiplication", "small"):   "9175",
    ("matrix_multiplication", "medium"):  "646700",
    ("matrix_multiplication", "large"):   "10291750",
}

# Java class names (PascalCase)
JAVA_CLASS = {
    "summation":             "Summation",
    "binary_search":         "BinarySearch",
    "merge_sort":            "MergeSort",
    "bfs":                   "BFS",
    "hash_table":            "HashTable",
    "matrix_multiplication": "MatrixMultiplication",
}


# ---------------------------------------------------------------------------
# Language definitions
# ---------------------------------------------------------------------------
# To add a new language, create a class with:
#   name          — display name
#   source(algo)  — path to source file
#   compile(algo) — return (cmd_list, exe_path), or None if interpreted
#   run(algo, size) — command list to execute
# Then append it to the LANGUAGES list at the bottom.
# ---------------------------------------------------------------------------

class LangC:
    name = "c"

    @staticmethod
    def source(algo):
        return os.path.join(IMPL_DIR, "c", f"{algo}.c")

    @staticmethod
    def compile(algo):
        src = LangC.source(algo)
        exe = os.path.join(BIN_DIR, f"{algo}_c.exe")
        return ["gcc", "-O2", "-o", exe, src], exe

    @staticmethod
    def run(algo, size):
        exe = os.path.join(BIN_DIR, f"{algo}_c.exe")
        return [exe, size]


# class LangPython:
#     name = "python"
#
#     @staticmethod
#     def source(algo):
#         return os.path.join(IMPL_DIR, "python", f"{algo}.py")
#
#     @staticmethod
#     def compile(algo):
#         return None  # interpreted
#
#     @staticmethod
#     def run(algo, size):
#         return ["python", LangPython.source(algo), size]


LANGUAGES = [LangC]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def timed_run(cmd, timeout=120):
    """Run a command, return (stdout, stderr, returncode, elapsed_s)."""
    t0 = time.perf_counter()
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        elapsed = time.perf_counter() - t0
        return result.stdout.strip(), result.stderr.strip(), result.returncode, elapsed
    except FileNotFoundError:
        return "", "binary not found", -1, time.perf_counter() - t0
    except subprocess.TimeoutExpired:
        return "", f"timeout after {timeout}s", -1, time.perf_counter() - t0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    os.makedirs(BIN_DIR, exist_ok=True)
    all_pass = True

    for lang in LANGUAGES:
        print("=" * 80)
        print(f"  {lang.name.upper()}")
        print("=" * 80)

        # --- Compile phase ---
        print("\n  Compiling...")
        build_ok = set()
        for algo in ALGORITHMS:
            src = lang.source(algo)
            if not os.path.exists(src):
                print(f"    SKIP  {algo} — source not found")
                continue

            compile_info = lang.compile(algo)
            if compile_info is None:
                build_ok.add(algo)
                continue

            cmd, _ = compile_info
            _, stderr, rc, elapsed = timed_run(cmd, timeout=30)
            if rc != 0:
                print(f"    FAIL  {algo} ({elapsed:.2f}s) — {stderr[:200]}")
            else:
                print(f"    OK    {algo} ({elapsed:.2f}s)")
                build_ok.add(algo)

        print(f"  {len(build_ok)}/{len(ALGORITHMS)} compiled OK.\n")

        # --- Run phase ---
        passes = 0
        fails = 0

        print(f"  {'ALGORITHM':<23s} {'SIZE':<8s} {'OUTPUT':<20s} {'TIME':>10s}  STATUS")
        print("  " + "-" * 75)

        for algo in ALGORITHMS:
            if algo not in build_ok:
                for size in SIZES:
                    fails += 1
                    print(f"  {algo:<23s} {size:<8s} {'—':<20s} {'—':>10s}  FAIL (not compiled)")
                continue

            for size in SIZES:
                cmd = lang.run(algo, size)
                stdout, stderr, rc, elapsed = timed_run(cmd)
                expected = EXPECTED.get((algo, size))
                time_str = f"{elapsed:.4f}s"

                if rc != 0:
                    status = f"FAIL (exit {rc})"
                    fails += 1
                    display = "—"
                elif expected is None:
                    status = "SKIP (no expected value)"
                    display = stdout
                elif stdout == expected:
                    status = "PASS"
                    passes += 1
                    display = stdout
                else:
                    status = f"FAIL (expected {expected})"
                    fails += 1
                    display = stdout

                print(f"  {algo:<23s} {size:<8s} {display:<20s} {time_str:>10s}  {status}")

        # --- Summary ---
        total = passes + fails
        print("  " + "-" * 75)
        print(f"  {passes} passed, {fails} failed out of {total}")
        print("=" * 80)

        if fails > 0:
            all_pass = False

    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
