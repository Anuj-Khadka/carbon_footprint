# -*- coding: utf-8 -*-
"""
verify_outputs.py
=================
Cross-language output correctness verification for carbon footprint research.

Strategy
--------
1. Compile & run the C implementation of each algorithm — this is the REFERENCE.
2. Compile & run every other language implementation of the same algorithm.
3. Compare each output line-by-line against the C reference.
4. Report PASS / FAIL per (language, algorithm, input_size) combination.
5. Write a JSON summary report to verify_outputs_report.json.

Algorithms   : summation, binary_search, merge_sort, bfs, hash_table, matrix_multiplication
Languages    : c (reference), rust, go, java, javascript, python
Input sizes  : small, medium, large  (encoded in each implementation's constants)

Directory layout expected
--------------------------
carbon_footprint/
  implementations/
    c/
      summation.c  binary_search.c  merge_sort.c  bfs.c  hash_table.c  matrix_multiplication.c
    rust/
      summation/src/main.rs
      binary_search/src/main.rs
      ... (each in own Cargo project)
    go/
      summation.go  ...
    java/
      Summation.java  BinarySearch.java  MergeSort.java  BFS.java  HashTable.java  MatrixMul.java
    javascript/
      summation.js  ...
    python/
      summation.py  ...

Each implementation uses hardcoded constants for input size (N/V constants in source).
Output is printed to stdout with no debug/formatting.

Usage
-----
    python detailed.py [--impl-dir PATH] [--report PATH] [--verbose] [--algo ALGO] [--lang LANG]

Defaults
--------
    --impl-dir  : ./implementations   (relative to this script)
    --report    : ./verify_outputs_report.json
    --algo      : all algorithms (summation, binary_search, merge_sort, bfs, hash_table, matrix_multiplication)
    --lang      : all languages (c, python, javascript, go, java, rust)
"""

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional
# Handle Windows encoding issues
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
# -------------------------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------------------------

ALGORITHMS = [
    "summation",
    "binary_search",
    "merge_sort",
    "bfs",
    "hash_table",
    "matrix_multiplication",
]

INPUT_SIZES = ["small", "medium", "large"]

# Java source files use PascalCase class names
JAVA_CLASS_NAMES = {
    "summation":     "Summation",
    "binary_search": "BinarySearch",
    "merge_sort":    "MergeSort",
    "bfs":           "BFS",
    "hash_table":    "HashTable",
    "matrix_multiplication":    "MatrixMul",
}

# Compiler / interpreter flags
C_COMPILE_FLAGS    = ["-O2", "-o"]          # gcc <src> -O2 -o <exe>
# Rust  : cargo run --quiet --release  (in project directory)
# Go    : go run <src>  (no explicit compile step needed for correctness check)
# Java  : javac <src>  then  java -server <class>
# JS    : node <src>
# Py    : python <src>

TIMEOUT_SECONDS = 60  # per subprocess call

ON_WINDOWS = platform.system() == "Windows"

# -------------------------------------------------------------------------------------
# Data structures
# -------------------------------------------------------------------------------------

@dataclass
class RunResult:
    language:   str
    algorithm:  str
    size:       str
    stdout:     str = ""
    stderr:     str = ""
    returncode: int = -1
    error:      str = ""   # high-level error (compile fail, timeout, not found …)
    duration_s: float = 0.0

@dataclass
class CompareResult:
    language:  str
    algorithm: str
    size:      str
    passed:    bool
    detail:    str = ""    # diff / mismatch description when failed

@dataclass
class Summary:
    total:   int = 0
    passed:  int = 0
    failed:  int = 0
    skipped: int = 0
    results: list = field(default_factory=list)

# -------------------------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------------------------

def find_exe(name: str) -> Optional[str]:
    """Return full path to an executable or None.
    
    For Rust tools (cargo, rustc), also checks ~/.cargo/bin on Windows/Unix.
    """
    # First try standard PATH
    exe = shutil.which(name)
    if exe:
        return exe
    
    # For Rust tools, also check ~/.cargo/bin (standard Rust installation location)
    if name in ("cargo", "rustc"):
        cargo_bin = Path.home() / ".cargo" / "bin" / name
        if ON_WINDOWS:
            cargo_bin = Path.home() / ".cargo" / "bin" / f"{name}.exe"
        if cargo_bin.exists():
            return str(cargo_bin)
    
    return None


def run_cmd(cmd: list[str], cwd: Optional[str] = None, env=None) -> tuple[int, str, str, float]:
    """Run a command, return (returncode, stdout, stderr, elapsed_seconds)."""
    t0 = time.perf_counter()
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
            cwd=cwd,
            env=env,
        )
        elapsed = time.perf_counter() - t0
        return proc.returncode, proc.stdout, proc.stderr, elapsed
    except subprocess.TimeoutExpired:
        elapsed = time.perf_counter() - t0
        return -1, "", f"TIMEOUT after {TIMEOUT_SECONDS}s", elapsed
    except Exception as exc:
        elapsed = time.perf_counter() - t0
        return -1, "", str(exc), elapsed


def normalise(output: str) -> list[str]:
    """Strip trailing whitespace from each line, drop blank lines at end."""
    lines = [line.rstrip() for line in output.splitlines()]
    while lines and lines[-1] == "":
        lines.pop()
    return lines


def diff_output(ref: list[str], got: list[str]) -> str:
    """Return a short human-readable diff or empty string if identical."""
    if ref == got:
        return ""
    lines = []
    max_show = 10
    for i, (r, g) in enumerate(zip(ref, got)):
        if r != g:
            lines.append(f"  line {i+1}: expected={r!r}  got={g!r}")
            if len(lines) >= max_show:
                lines.append("  … (more differences truncated)")
                break
    if len(ref) != len(got):
        lines.append(f"  line count: expected={len(ref)}  got={len(got)}")
    return "\n".join(lines)

# -------------------------------------------------------------------------------------
# Language runners
# -------------------------------------------------------------------------------------

class Runner:
    def __init__(self, impl_dir: Path, verbose: bool = False):
        self.impl_dir = impl_dir
        self.verbose  = verbose
        self._tmpdir  = tempfile.mkdtemp(prefix="verify_outputs_")

    def _log(self, msg: str):
        if self.verbose:
            print(f"  [dbg] {msg}", flush=True)

    def _src(self, language: str, algorithm: str) -> Optional[Path]:
        """Return path to source file, or None if missing."""
        if language == "rust":
            # Rust uses Cargo projects: rust/{algorithm}/src/main.rs
            path = self.impl_dir / "rust" / algorithm / "src" / "main.rs"
            return path if path.exists() else None
        
        ext_map = {
            "c":          f"{algorithm}.c",
            "go":         f"{algorithm}.go",
            "java":       f"{JAVA_CLASS_NAMES[algorithm]}.java",
            "javascript": f"{algorithm}.js",
            "python":     f"{algorithm}.py",
        }
        path = self.impl_dir / language / ext_map[language]
        return path if path.exists() else None

    # -- C --

    def run_c(self, algorithm: str, size: str) -> RunResult:
        r = RunResult("c", algorithm, size)
        src = self._src("c", algorithm)
        if src is None:
            r.error = f"Source not found: {self.impl_dir}/c/{algorithm}.c"
            return r

        gcc = find_exe("gcc")
        if gcc is None:
            r.error = "gcc not found in PATH"
            return r

        exe = os.path.join(self._tmpdir, f"c_{algorithm}" + (".exe" if ON_WINDOWS else ""))
        rc, out, err, _ = run_cmd([gcc, str(src)] + C_COMPILE_FLAGS + [exe])
        if rc != 0:
            r.error = f"Compile error:\n{err}"
            return r

        rc, out, err, elapsed = run_cmd([exe])
        r.returncode = rc
        r.stdout     = out
        r.stderr     = err
        r.duration_s = elapsed
        if rc != 0:
            r.error = f"Runtime error (rc={rc}):\n{err}"
        return r

    # -- Rust --

    def run_rust(self, algorithm: str, size: str) -> RunResult:
        r = RunResult("rust", algorithm, size)
        src = self._src("rust", algorithm)
        if src is None:
            r.error = f"Source not found: {self.impl_dir}/rust/{algorithm}/src/main.rs"
            return r

        cargo = find_exe("cargo")
        if cargo is None:
            r.error = "cargo not found in PATH"
            return r

        cargo_dir = src.parent.parent  # Go up from src/main.rs to project root
        rc, out, err, elapsed = run_cmd([cargo, "run", "--quiet", "--release"], cwd=str(cargo_dir))
        r.returncode = rc
        r.stdout     = out
        r.stderr     = err
        r.duration_s = elapsed
        if rc != 0:
            r.error = f"Runtime error (rc={rc}):\n{err}"
        return r

    # -- Go --

    def run_go(self, algorithm: str, size: str) -> RunResult:
        r = RunResult("go", algorithm, size)
        src = self._src("go", algorithm)
        if src is None:
            r.error = f"Source not found: {self.impl_dir}/go/{algorithm}.go"
            return r

        go_exe = find_exe("go")
        if go_exe is None:
            r.error = "go not found in PATH"
            return r

        rc, out, err, elapsed = run_cmd([go_exe, "run", str(src)])
        r.returncode = rc
        r.stdout     = out
        r.stderr     = err
        r.duration_s = elapsed
        if rc != 0:
            r.error = f"Runtime error (rc={rc}):\n{err}"
        return r

    # -- Java --

    def run_java(self, algorithm: str, size: str) -> RunResult:
        r = RunResult("java", algorithm, size)
        src = self._src("java", algorithm)
        if src is None:
            r.error = f"Source not found: {self.impl_dir}/java/{JAVA_CLASS_NAMES[algorithm]}.java"
            return r

        javac = find_exe("javac")
        java  = find_exe("java")
        if javac is None or java is None:
            r.error = "javac or java not found in PATH"
            return r

        # Compile into a temp dir so .class files don't pollute source tree
        java_out = os.path.join(self._tmpdir, f"java_{algorithm}")
        os.makedirs(java_out, exist_ok=True)
        rc, out, err, _ = run_cmd([javac, "-d", java_out, str(src)])
        if rc != 0:
            r.error = f"Compile error:\n{err}"
            return r

        class_name = JAVA_CLASS_NAMES[algorithm]
        rc, out, err, elapsed = run_cmd(
            [java, "-server", "-cp", java_out, class_name]
        )
        r.returncode = rc
        r.stdout     = out
        r.stderr     = err
        r.duration_s = elapsed
        if rc != 0:
            r.error = f"Runtime error (rc={rc}):\n{err}"
        return r

    # -- JavaScript --

    def run_javascript(self, algorithm: str, size: str) -> RunResult:
        r = RunResult("javascript", algorithm, size)
        src = self._src("javascript", algorithm)
        if src is None:
            r.error = f"Source not found: {self.impl_dir}/javascript/{algorithm}.js"
            return r

        node = find_exe("node")
        if node is None:
            r.error = "node not found in PATH"
            return r

        rc, out, err, elapsed = run_cmd([node, str(src)])
        r.returncode = rc
        r.stdout     = out
        r.stderr     = err
        r.duration_s = elapsed
        if rc != 0:
            r.error = f"Runtime error (rc={rc}):\n{err}"
        return r

    # -- Python --

    def run_python(self, algorithm: str, size: str) -> RunResult:
        r = RunResult("python", algorithm, size)
        src = self._src("python", algorithm)
        if src is None:
            r.error = f"Source not found: {self.impl_dir}/python/{algorithm}.py"
            return r

        python = find_exe("python") or find_exe("python3")
        if python is None:
            r.error = "python / python3 not found in PATH"
            return r

        rc, out, err, elapsed = run_cmd([python, str(src)])
        r.returncode = rc
        r.stdout     = out
        r.stderr     = err
        r.duration_s = elapsed
        if rc != 0:
            r.error = f"Runtime error (rc={rc}):\n{err}"
        return r

    # -- Dispatch --

    def run(self, language: str, algorithm: str, size: str) -> RunResult:
        dispatch = {
            "c":          self.run_c,
            "rust":       self.run_rust,
            "go":         self.run_go,
            "java":       self.run_java,
            "javascript": self.run_javascript,
            "python":     self.run_python,
        }
        fn = dispatch.get(language)
        if fn is None:
            r = RunResult(language, algorithm, size)
            r.error = f"Unknown language: {language}"
            return r
        self._log(f"run {language:12s} {algorithm:14s} {size}")
        return fn(algorithm, size)

    def cleanup(self):
        import shutil as _sh
        _sh.rmtree(self._tmpdir, ignore_errors=True)

# ─────────────────────────────────────────────────────────────────────────────
# Verification logic
# ─────────────────────────────────────────────────────────────────────────────

LANGUAGES_NON_REF = ["rust", "go", "java", "javascript", "python"]


def verify_all(impl_dir: Path, verbose: bool = False) -> Summary:
    runner  = Runner(impl_dir, verbose=verbose)
    summary = Summary()

    # Cache C reference outputs
    c_reference: dict[tuple[str, str], RunResult] = {}
    print("\n── Building C reference outputs ──────────────────────────────────")
    for algo in ALGORITHMS:
        for size in INPUT_SIZES:
            key = (algo, size)
            res = runner.run("c", algo, size)
            c_reference[key] = res
            status = "OK" if res.returncode == 0 and not res.error else "FAIL"
            print(f"  C  {algo:14s}  {size:6s}  [{status}]")
            if res.error:
                print(f"     Error: {res.error}")
            if res.stdout:
                print(f"     Output: {res.stdout.strip()}")

    print("\n── Verifying non-reference languages ────────────────────────────")
    for lang in LANGUAGES_NON_REF:
        print(f"\n  {lang.upper()}")
        for algo in ALGORITHMS:
            for size in INPUT_SIZES:
                summary.total += 1
                ref = c_reference[(algo, size)]

                # If C reference failed, we can't compare — skip
                if ref.error or ref.returncode != 0:
                    cr = CompareResult(lang, algo, size, False,
                                       "C reference failed — cannot compare")
                    summary.skipped += 1
                    summary.results.append(asdict(cr))
                    print(f"    {algo:14s}  {size:6s}  [SKIP] (C reference unavailable)")
                    continue

                got = runner.run(lang, algo, size)

                if got.error or got.returncode != 0:
                    detail = got.error or f"Non-zero exit: {got.returncode}\n{got.stderr}"
                    cr = CompareResult(lang, algo, size, False, detail)
                    summary.failed += 1
                    summary.results.append(asdict(cr))
                    print(f"    {algo:14s}  {size:6s}  [FAIL] {detail.splitlines()[0]}")
                    if got.stdout:
                        print(f"      Output: {got.stdout.strip()}")
                    continue

                ref_lines = normalise(ref.stdout)
                got_lines = normalise(got.stdout)
                diff      = diff_output(ref_lines, got_lines)

                if diff == "":
                    cr = CompareResult(lang, algo, size, True)
                    summary.passed += 1
                    print(f"    {algo:14s}  {size:6s}  [PASS]  ({got.duration_s:.3f}s)")
                    if got.stdout:
                        print(f"      Output: {got.stdout.strip()}")
                else:
                    cr = CompareResult(lang, algo, size, False, diff)
                    summary.failed += 1
                    print(f"    {algo:14s}  {size:6s}  [FAIL]")
                    print(f"      Expected: {normalise(ref.stdout)[0] if ref.stdout else '(empty)'}")
                    print(f"      Got:      {normalise(got.stdout)[0] if got.stdout else '(empty)'}")
                    if got.stdout:
                        print(f"      Output: {got.stdout.strip()}")
                    if verbose:
                        print(diff)

                summary.results.append(asdict(cr))

    runner.cleanup()
    return summary

# ─────────────────────────────────────────────────────────────────────────────
# Report
# ─────────────────────────────────────────────────────────────────────────────

def print_summary(s: Summary):
    print("\n" + "═" * 60)
    print("VERIFICATION SUMMARY")
    print("═" * 60)
    print(f"  Total comparisons : {s.total}")
    print(f"  PASSED            : {s.passed}")
    print(f"  FAILED            : {s.failed}")
    print(f"  SKIPPED           : {s.skipped}")
    print("═" * 60)

    if s.failed:
        print("\nFailed cases:")
        for r in s.results:
            if not r["passed"] and r["detail"] != "C reference failed — cannot compare":
                print(f"  {r['language']:12s}  {r['algorithm']:14s}  {r['size']:6s}")
                for line in r["detail"].splitlines()[:5]:
                    print(f"      {line}")


def save_report(s: Summary, path: Path):
    report = {
        "total":   s.total,
        "passed":  s.passed,
        "failed":  s.failed,
        "skipped": s.skipped,
        "results": s.results,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"\nReport saved → {path}")

# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def parse_args():
    here = Path(__file__).parent
    p = argparse.ArgumentParser(
        description="Cross-language output correctness verifier (C = reference baseline)."
    )
    p.add_argument(
        "--impl-dir",
        default=str(here / "implementations"),
        help="Root folder containing per-language sub-folders (default: ./implementations)",
    )
    p.add_argument(
        "--report",
        default=str(here / "verify_outputs_report.json"),
        help="Where to write the JSON report (default: ./verify_outputs_report.json)",
    )
    p.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print compiler output, diffs, and debug info",
    )
    p.add_argument(
        "--algo",
        choices=ALGORITHMS,
        default=None,
        help="Run only one algorithm (default: all)",
    )
    p.add_argument(
        "--size",
        choices=INPUT_SIZES,
        default=None,
        help="Run only one input size (default: all)",
    )
    p.add_argument(
        "--lang",
        choices=LANGUAGES_NON_REF,
        default=None,
        help="Test only one non-reference language (default: all)",
    )
    return p.parse_args()


def main():
    args = parse_args()

    # Honour single-algo / single-size / single-lang filters
    global ALGORITHMS, INPUT_SIZES, LANGUAGES_NON_REF
    if args.algo:
        ALGORITHMS = [args.algo]
    if args.size:
        INPUT_SIZES = [args.size]
    if args.lang:
        LANGUAGES_NON_REF = [args.lang]

    impl_dir = Path(args.impl_dir)
    if not impl_dir.exists():
        print(f"ERROR: --impl-dir '{impl_dir}' does not exist.", file=sys.stderr)
        sys.exit(1)

    print(f"Implementation directory : {impl_dir.resolve()}")
    print(f"Algorithms               : {', '.join(ALGORITHMS)}")
    print(f"Input sizes              : {', '.join(INPUT_SIZES)}")
    print(f"Languages (vs C ref)     : {', '.join(LANGUAGES_NON_REF)}")

    summary = verify_all(impl_dir, verbose=args.verbose)
    print_summary(summary)
    save_report(summary, Path(args.report))

    sys.exit(0 if summary.failed == 0 else 1)


if __name__ == "__main__":
    main()