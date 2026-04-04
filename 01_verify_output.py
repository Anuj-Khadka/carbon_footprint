"""
verify_output.py
---------------
Compiles and runs algorithm implementations across languages.
Verifies output correctness against C reference values and reports timing.

Usage:
    python verify_output.py
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

SIZES = ["small", "mid", "large"]

# C reference outputs — every language must match these
EXPECTED = {
    ("summation",               "small"):           "5050",
    ("summation",               "mid"):             "50005000",
    ("summation",               "large"):           "500000500000",
    ("binary_search",           "small"):           "99",
    ("binary_search",           "mid"):             "9999",
    ("binary_search",           "large"):           "999999",
    ("merge_sort",              "small"):           "100",
    ("merge_sort",              "mid"):             "10000",
    ("merge_sort",              "large"):           "1000000",
    ("bfs",                     "small"):           "100",
    ("bfs",                     "mid"):             "1000",
    ("bfs",                     "large"):           "5000",
    ("hash_table",              "small"):           "64850",
    ("hash_table",              "mid"):             "649985000",
    ("hash_table",              "large"):           "64999850000",
    ("matrix_multiplication",   "small"):           "9175",
    ("matrix_multiplication",   "mid"):             "646700",
    ("matrix_multiplication",   "large"):           "10291750",
}



def compile_c(algo, size):
    """Compile a single C file. Returns (success, error_message)."""
    src = os.path.join(IMPL_DIR, "c", algo, f"{algo}_{size}.c")
    exe = os.path.join(BIN_DIR,  f"{algo}_{size}_c.exe")
 
    if not os.path.exists(src):
        return False, exe, f"source not found: {src}"
 
    cmd = ["gcc", "-O2", "-o", exe, src]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return False, exe, result.stderr.strip()
        return True, exe, ""
    except FileNotFoundError:
        return False, exe, "gcc not found"
    except subprocess.TimeoutExpired:
        return False, exe, "compile timeout"
 
 
def run_once(exe, timeout=10):
    """
    Launch exe, wait for 'ready', send one newline trigger,
    read the checksum line. Returns (checksum, elapsed_s, error).
    """
    try:
        proc = subprocess.Popen(
            [exe],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
 
        # Wait for ready
        t0 = time.perf_counter()
        ready_line = proc.stdout.readline()
        if ready_line.strip() != "ready":
            proc.kill()
            return "", 0.0, f"expected 'ready', got: {ready_line.strip()!r}"
 
        # Arm timer, send trigger
        t1 = time.perf_counter()
        proc.stdin.write("\n")
        proc.stdin.flush()
 
        # Read checksum
        checksum_line = proc.stdout.readline()
        elapsed = time.perf_counter() - t1
 
        proc.kill()
        proc.wait()
 
        return checksum_line.strip(), elapsed, ""
 
    except FileNotFoundError:
        return "", 0.0, "binary not found"
    except subprocess.TimeoutExpired:
        return "", 0.0, f"timeout after {timeout}s"
    except Exception as e:
        return "", 0.0, str(e)
 
 
def main():
    os.makedirs(BIN_DIR, exist_ok=True)
 
    passes = 0
    fails  = 0
 
    print("=" * 80)
    print("  C — COMPILE")
    print("=" * 80)
 
    # Compile all files first
    compiled = {}  # (algo, size) -> exe path
    for algo in ALGORITHMS:
        for size in SIZES:
            ok, exe, err = compile_c(algo, size)
            label = f"{algo}_{size}"
            if ok:
                compiled[(algo, size)] = exe
                print(f"  OK    {label}")
            else:
                print(f"  FAIL  {label} — {err}")
 
    total_files = len(ALGORITHMS) * len(SIZES)
    print(f"\n  {len(compiled)}/{total_files} compiled OK.\n")
 
    # Run and verify
    print("=" * 80)
    print("  C — RUN & VERIFY")
    print("=" * 80)
    print(f"\n  {'ALGORITHM':<25s} {'SIZE':<8s} {'OUTPUT':<20s} {'TIME':>10s}  STATUS")
    print("  " + "-" * 75)
 
    for algo in ALGORITHMS:
        for size in SIZES:
            if (algo, size) not in compiled:
                fails += 1
                print(f"  {algo:<25s} {size:<8s} {'—':<20s} {'—':>10s}  FAIL (not compiled)")
                continue
 
            exe = compiled[(algo, size)]
            checksum, elapsed, err = run_once(exe)
            expected = EXPECTED.get((algo, size))
            time_str = f"{elapsed:.4f}s"
 
            if err:
                status = f"FAIL ({err})"
                fails += 1
                display = "—"
            elif checksum == expected:
                status = "PASS"
                passes += 1
                display = checksum
            else:
                status = f"FAIL (expected {expected}, got {checksum})"
                fails += 1
                display = checksum
 
            print(f"  {algo:<25s} {size:<8s} {display:<20s} {time_str:>10s}  {status}")
 
    total = passes + fails
    print("  " + "-" * 75)
    print(f"\n  {passes} passed, {fails} failed out of {total}")
    print("=" * 80)
 
    sys.exit(0 if fails == 0 else 1)
 
 
if __name__ == "__main__":
    main()