"""
02_verify_outputs_others.py
---------------------------
Compiles and runs algorithm implementations for Python, JavaScript, Java, Go, and Rust.
Verifies output correctness against C reference values.

Usage:
    python 02_verify_outputs_others.py
"""

import subprocess
import os
import sys
import time
import re

ROOT     = os.path.dirname(os.path.abspath(__file__))
IMPL_DIR = os.path.join(ROOT, "implementations")
BIN_DIR  = os.path.join(ROOT, "implementations", "build")

ALGORITHMS = [
    "summation",
    "binary_search",
    "merge_sort",
    "bfs",
    "hash_table",
    "matrix_multiplication",
]

SIZES = ["small", "mid", "large"]

EXPECTED = {
    ("summation",             "small"):  "5050",
    ("summation",             "mid"):    "50005000",
    ("summation",             "large"):  "500000500000",
    ("binary_search",         "small"):  "99",
    ("binary_search",         "mid"):    "9999",
    ("binary_search",         "large"):  "999999",
    ("merge_sort",            "small"):  "100",
    ("merge_sort",            "mid"):    "10000",
    ("merge_sort",            "large"):  "1000000",
    ("bfs",                   "small"):  "100",
    ("bfs",                   "mid"):    "1000",
    ("bfs",                   "large"):  "5000",
    ("hash_table",            "small"):  "64850",
    ("hash_table",            "mid"):    "649985000",
    ("hash_table",            "large"):  "64999850000",
    ("matrix_multiplication", "small"):  "9175",
    ("matrix_multiplication", "mid"):    "646700",
    ("matrix_multiplication", "large"):  "10291750",
}

JAVA_CLASS = {
    ("summation",             "small"):  "Summation_Small",
    ("summation",             "mid"):    "Summation_Mid",
    ("summation",             "large"):  "Summation_Large",
    ("binary_search",         "small"):  "BinarySearch_Small",
    ("binary_search",         "mid"):    "BinarySearch_Mid",
    ("binary_search",         "large"):  "BinarySearch_Large",
    ("merge_sort",            "small"):  "MergeSort_Small",
    ("merge_sort",            "mid"):    "MergeSort_Mid",
    ("merge_sort",            "large"):  "MergeSort_Large",
    ("bfs",                   "small"):  "BFS_Small",
    ("bfs",                   "mid"):    "BFS_Mid",
    ("bfs",                   "large"):  "BFS_Large",
    ("hash_table",            "small"):  "HashTable_Small",
    ("hash_table",            "mid"):    "HashTable_Mid",
    ("hash_table",            "large"):  "HashTable_Large",
    ("matrix_multiplication", "small"):  "MatrixMultiplication_Small",
    ("matrix_multiplication", "mid"):    "MatrixMultiplication_Mid",
    ("matrix_multiplication", "large"):  "MatrixMultiplication_Large",
}


class LangPython:
    name = "Python"

    @staticmethod
    def source(algo, size):
        return os.path.join(IMPL_DIR, "python", algo, f"{algo}_{size}.py")

    @staticmethod
    def compile(algo, size):
        return None

    @staticmethod
    def run(algo, size):
        return ["python", LangPython.source(algo, size)]


class LangJavaScript:
    name = "JavaScript"

    @staticmethod
    def source(algo, size):
        return os.path.join(IMPL_DIR, "javascript", algo, f"{algo}_{size}.js")

    @staticmethod
    def compile(algo, size):
        return None

    @staticmethod
    def run(algo, size):
        return ["node", LangJavaScript.source(algo, size)]


class LangJava:
    name = "Java"

    @staticmethod
    def source(algo, size):
        cls = JAVA_CLASS[(algo, size)]
        return os.path.join(IMPL_DIR, "java", algo, f"{cls}.java")
    @staticmethod
    def package_name(algo, size):
        """Read optional Java package declaration from source file."""
        src = LangJava.source(algo, size)
        try:
            with open(src, "r", encoding="utf-8") as f:
                # Package declarations are expected near the top of the file.
                for _ in range(20):
                    line = f.readline()
                    if not line:
                        break
                    m = re.match(r"\s*package\s+([A-Za-z_][A-Za-z0-9_\.]*)\s*;", line)
                    if m:
                        return m.group(1)
        except OSError:
            return ""
        return ""

    @staticmethod
    def compile(algo, size):
        src = LangJava.source(algo, size)
        out_dir = os.path.join(IMPL_DIR, "java", algo)
        return ["javac", "-d", out_dir, src]

    @staticmethod
    def run(algo, size):
        cls = JAVA_CLASS[(algo, size)]
        cp  = os.path.join(IMPL_DIR, "java", algo)
        pkg = LangJava.package_name(algo, size)
        fqcn = f"{pkg}.{cls}" if pkg else cls
        return ["java", "-Xss4m", "-cp", cp, fqcn]


class LangGo:
    name = "Go"

    @staticmethod
    def source(algo, size):
        return os.path.join(IMPL_DIR, "go", algo, size, f"{algo}_{size}.go")

    @staticmethod
    def compile(algo, size):
        src = LangGo.source(algo, size)
        exe = os.path.join(BIN_DIR, f"{algo}_{size}_go.exe")
        return ["go", "build", "-o", exe, src]

    @staticmethod
    def run(algo, size):
        return [os.path.join(BIN_DIR, f"{algo}_{size}_go.exe")]


class LangRust:
    name = "Rust"

    @staticmethod
    def source(algo, size):
        return os.path.join(IMPL_DIR, "rust", algo, size, f"{algo}_{size}.rs")

    @staticmethod
    def compile(algo, size):
        src = LangRust.source(algo, size)
        exe = os.path.join(BIN_DIR, f"{algo}_{size}_rust.exe")
        return ["rustc", "-O", "-o", exe, src]

    @staticmethod
    def run(algo, size):
        return [os.path.join(BIN_DIR, f"{algo}_{size}_rust.exe")]


# LANGUAGES = [LangPython, LangJavaScript, LangJava, LangGo, LangRust]
LANGUAGES = [LangRust]


def compile_one(lang, algo, size, timeout=60):
    src = lang.source(algo, size)
    if not os.path.exists(src):
        return False, f"source not found: {src}"

    cmd = lang.compile(algo, size)
    if cmd is None:
        return True, ""

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if result.returncode != 0:
            return False, result.stderr.strip()[:200]
        return True, ""
    except FileNotFoundError:
        return False, f"compiler not found: {cmd[0]}"
    except subprocess.TimeoutExpired:
        return False, "compile timeout"


def run_once(cmd, timeout=30):
    """
    Launch program, wait for 'ready', send one newline trigger,
    close stdin so the process exits after one run, read checksum.
    Returns (checksum, elapsed_ms, error).
    """
    proc = None
    try:
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # Wait for "ready"
        ready_line = proc.stdout.readline()
        if ready_line.strip() != "ready":
            proc.kill()
            proc.wait()
            return "", 0.0, f"expected 'ready', got: {ready_line.strip()!r}"

        # Arm timer, send trigger, close stdin
        t0 = time.perf_counter()
        proc.stdin.write("\n")
        proc.stdin.flush()
        proc.stdin.close()  # EOF — process exits after one iteration

        # Read checksum
        checksum_line = proc.stdout.readline()
        elapsed_ms = (time.perf_counter() - t0) * 1000

        proc.wait(timeout=timeout)
        return checksum_line.strip(), elapsed_ms, ""

    except FileNotFoundError:
        return "", 0.0, f"binary not found: {cmd[0]}"
    except subprocess.TimeoutExpired:
        if proc:
            proc.kill()
            proc.wait()
        return "", 0.0, f"timeout after {timeout}s"
    except Exception as e:
        if proc:
            proc.kill()
            proc.wait()
        return "", 0.0, str(e)


def print_header(title):
    print("=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_table_header():
    print(f"\n  {'ALGORITHM':<25s} {'SIZE':<8s} {'OUTPUT':<20s} {'TIME':>10s}  STATUS")
    print("  " + "-" * 75)


def print_table_footer(passes, fails):
    print("  " + "-" * 75)
    print(f"\n  {passes} passed, {fails} failed out of {passes + fails}")
    print("=" * 80)


def main():
    os.makedirs(BIN_DIR, exist_ok=True)

    total_passes = 0
    total_fails  = 0

    for lang in LANGUAGES:
        print_header(f"{lang.name.upper()} — COMPILE")

        compiled      = set()
        needs_compile = lang.compile("summation", "small") is not None

        if needs_compile:
            for algo in ALGORITHMS:
                for size in SIZES:
                    ok, err = compile_one(lang, algo, size)
                    label   = f"{algo}_{size}"
                    if ok:
                        compiled.add((algo, size))
                        print(f"  OK    {label}")
                    else:
                        print(f"  FAIL  {label} — {err}")
            print(f"\n  {len(compiled)}/{len(ALGORITHMS) * len(SIZES)} compiled OK.")
        else:
            for algo in ALGORITHMS:
                for size in SIZES:
                    if os.path.exists(lang.source(algo, size)):
                        compiled.add((algo, size))
                    else:
                        print(f"  MISS  {algo}_{size} — source not found")
            print(f"  {len(compiled)}/{len(ALGORITHMS) * len(SIZES)} source files found.")

        print_header(f"{lang.name.upper()} — RUN & VERIFY")
        print_table_header()

        passes = 0
        fails  = 0

        for algo in ALGORITHMS:
            for size in SIZES:
                if (algo, size) not in compiled:
                    fails += 1
                    print(f"  {algo:<25s} {size:<8s} {'—':<20s} {'—':>10s}  FAIL (not compiled)")
                    continue

                checksum, elapsed_ms, err = run_once(lang.run(algo, size))
                expected = EXPECTED.get((algo, size))
                time_str = f"{elapsed_ms:.3f}ms"

                if err:
                    status  = f"FAIL ({err})"
                    fails  += 1
                    display = "—"
                elif checksum == expected:
                    status  = "PASS"
                    passes += 1
                    display = checksum
                else:
                    status  = f"FAIL (got {checksum!r}, expected {expected!r})"
                    fails  += 1
                    display = checksum

                print(f"  {algo:<25s} {size:<8s} {display:<20s} {time_str:>10s}  {status}")

        print_table_footer(passes, fails)
        total_passes += passes
        total_fails  += fails

    print_header("GRAND SUMMARY")
    print(f"\n  Total: {total_passes} passed, {total_fails} failed out of {total_passes + total_fails}")
    print("=" * 80)

    sys.exit(0 if total_fails == 0 else 1)


if __name__ == "__main__":
    main()