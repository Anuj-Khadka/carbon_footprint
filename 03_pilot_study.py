"""
pilot_study.py  –  Carbon Footprint Benchmark  (build-up version)
Step 1: LHM sensor reading
Step 2: Program execution
Step 3: Full pilot loop (50 runs per cell, 5 warm-ups discarded)
"""

import csv
import random
import sys
from datetime import datetime
from pathlib import Path
import requests
import time
import subprocess


LHM_URL        = "http://172.22.1.29:8085/data.json"
BASE_DIR       = Path(r"C:\Users\Stemadmin\Desktop\Anuj Khadka\carbon_footprint\implementations")
RESULTS_DIR    = Path(r"C:\Users\Stemadmin\Desktop\Anuj Khadka\carbon_footprint\results")
BUILD_DIR    = BASE_DIR / "build"
 
WARM_UP_RUNS   = 5
PILOT_RUNS     = 50
INTER_RUN_SLEEP = 0.05   # seconds between iterations (within a cell)


LANGUAGES = ["c", "rust", "go", "java", "javascript", "python"]
ALGORITHMS = ["summation", "binary_search", "merge_sort", "bfs", "hash_table", "matrix_multiplication"]
SIZES      = ["small", "mid", "large"]

JAVA_CLASS = {
    "summation":             "Summation",
    "binary_search":         "BinarySearch",
    "merge_sort":            "MergeSort",
    "bfs":                   "BFS",
    "hash_table":            "HashTable",
    "matrix_multiplication": "MatrixMultiplication",
}

JAVA_SIZE = {"small": "Small", "mid": "Mid", "large": "Large"}

COMMANDS = {
    "c":          lambda algo, size: [str(BUILD_DIR / f"{algo}_{size}_c.exe")],
    "rust":       lambda algo, size: [str(BUILD_DIR / f"{algo}_{size}_rust.exe")],
    "go":         lambda algo, size: [str(BUILD_DIR / f"{algo}_{size}_go.exe")],
    "java":       lambda algo, size: ["java", "-Xss4m", "-cp", str(BASE_DIR / "java"), f"{algo}.{JAVA_CLASS[algo]}_{JAVA_SIZE[size]}"],
    "javascript": lambda algo, size: ["node", str(BASE_DIR / "javascript" / algo / f"{algo}_{size}.js")],
    "python":     lambda algo, size: [sys.executable, str(BASE_DIR / "python"   / algo / f"{algo}_{size}.py")],
}


def run_build(cmd: list[str], timeout: int = 120) -> tuple[bool, str]:
    try:
        completed = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except FileNotFoundError:
        return False, f"tool not found: {cmd[0]}"
    except subprocess.TimeoutExpired:
        return False, "build timed out"

    if completed.returncode != 0:
        msg = completed.stderr.strip() or completed.stdout.strip() or f"exit code {completed.returncode}"
        return False, msg
    return True, ""


def preflight_build() -> None:
    """Build Rust/Go/Java artifacts once before measurement runs."""
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    build_errors = []

    print("\n=== Preflight build (Rust/Go/Java) ===")
    for algo in ALGORITHMS:
        for size in SIZES:
            rust_src = BASE_DIR / "rust" / algo / size / f"{algo}_{size}.rs"
            rust_exe = BUILD_DIR / f"{algo}_{size}_rust.exe"
            ok, err = run_build(["rustc", "-O", "-o", str(rust_exe), str(rust_src)])
            if not ok:
                build_errors.append(("rust", algo, size, err))

            go_src = BASE_DIR / "go" / algo / size / f"{algo}_{size}.go"
            go_exe = BUILD_DIR / f"{algo}_{size}_go.exe"
            ok, err = run_build(["go", "build", "-o", str(go_exe), str(go_src)])
            if not ok:
                build_errors.append(("go", algo, size, err))

            java_src = BASE_DIR / "java" / algo / f"{JAVA_CLASS[algo]}_{JAVA_SIZE[size]}.java"
            ok, err = run_build(["javac", "-d", str(BASE_DIR / "java"), str(java_src)])
            if not ok:
                build_errors.append(("java", algo, size, err))

    if build_errors:
        summary_lines = [f"{lang}/{algo}/{size}: {msg}" for lang, algo, size, msg in build_errors[:8]]
        if len(build_errors) > 8:
            summary_lines.append(f"... and {len(build_errors) - 8} more build errors")
        summary = "\n  ".join(summary_lines)
        raise RuntimeError(f"Preflight build failed ({len(build_errors)} errors):\n  {summary}")

    print("Preflight build complete.")


######################### LHM ###############################

def get_cpu_package_watts() -> float:
    response = requests.get(LHM_URL)

    data = response.json() 
    # print(data)

    def search(node: dict) -> float | None:
        if node.get("SensorId") == "/intelcpu/0/power/0":
            try:
                return float(node["Value"].split()[0])
            except (ValueError, IndexError):
                pass
        for child in node.get("Children", []):
            result = search(child)
            if result is not None:
                return result
        return None
 
    watts = search(data)
    if watts is None:
        raise RuntimeError("CPU Package power sensor not found in LHM response.")
    return watts


def run_once(proc: subprocess.Popen):
    """
    Run one algorithm iteration using the stdin handshake protocol.
 
    Sequence:
      1. Read watts before  (RAPL window open)
      2. Send newline to trigger the algorithm
      3. Wait for the checksum line back
      4. Read watts after   (RAPL window close)
 
    Returns (energy_joules, checksum_str).
    """

    w_before = get_cpu_package_watts()


    t_before = time.perf_counter()

    # Trigger the algorithm to run
    proc.stdin.write("\n")
    proc.stdin.flush()

    # Wait for the checksum line back
    checksum_line = proc.stdout.readline().strip()

    t_after = time.perf_counter()
    w_after = get_cpu_package_watts()

    elapsed_time = t_after - t_before
    avg_watts = (w_before + w_after) / 2
    energy_joules = avg_watts * elapsed_time

    return energy_joules, checksum_line


def run_cell(language: str, algorithm:str, size: str):
    """
    Returns a list of result dicts (one per measured run).
       
    """

    cmd = COMMANDS[language](algorithm, size)
    print(f"  Launching: {' '.join(cmd)}")
 
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )

    # Wait for ready signal
    ready = proc.stdout.readline().strip()
    if ready != "ready":
        stderr_out = proc.stderr.read()
        proc.terminate()
        msg = f"Expected 'ready', got '{ready!r}' for {language}/{algorithm}/{size}"
        if stderr_out.strip():
            msg += f"\n    stderr: {stderr_out.strip()}"
        raise RuntimeError(msg)
 
    # Warm-up runs (discarded)
    for _ in range(WARM_UP_RUNS):
        run_once(proc)
        time.sleep(INTER_RUN_SLEEP)
 
    # Measured runs
    results = []
    for run_idx in range(1, PILOT_RUNS + 1):
        joules, checksum = run_once(proc)
        results.append({
            "language":  language,
            "algorithm": algorithm,
            "size":      size,
            "run":       run_idx,
            "joules":    joules,
            "checksum":  checksum,
        })
        time.sleep(INTER_RUN_SLEEP)
 
    proc.stdin.close()
    try:
        proc.wait(timeout=30)
    except subprocess.TimeoutExpired:
        proc.kill()
        raise RuntimeError(f"Process did not exit within 30s: {language}/{algorithm}/{size}")
    return results



def main():
    sys.stdout.reconfigure(line_buffering=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    # preflight_build()
    timestamp   = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = RESULTS_DIR / f"pilot_{timestamp}.csv"
 
    # Build all cells and shuffle to randomise order
    cells = [
        (lang, algo, size)
        for lang  in LANGUAGES
        for algo  in ALGORITHMS
        for size  in SIZES
    ]
    random.shuffle(cells)
 
    fieldnames = ["language", "algorithm", "size", "run", "joules", "checksum"]
    errors     = []
 
    with open(output_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
 
        total = len(cells)
        for idx, (lang, algo, size) in enumerate(cells, 1):
            print(f"\n[{idx}/{total}] {lang} / {algo} / {size}")
            try:
                rows = run_cell(lang, algo, size)
 
                # Verify all checksums match
                checksums = {r["checksum"] for r in rows}
                if len(checksums) > 1:
                    print(f"  WARNING: inconsistent checksums: {checksums}")
                else:
                    print(f"  Checksum ✓  ({checksums.pop()})")
 
                writer.writerows(rows)
                f.flush()
 
                avg_mj = sum(r["joules"] for r in rows) / len(rows) * 1000
                print(f"  Avg energy: {avg_mj:.4f} mJ over {len(rows)} runs")
 
            except Exception as e:
                print(f"  ERROR: {e}")
                errors.append((lang, algo, size, str(e)))
 
    print(f"\n{'='*60}")
    print(f"Pilot complete. Results saved to:\n  {output_file}")
    if errors:
        print(f"\nFailed cells ({len(errors)}):")
        for lang, algo, size, msg in errors:
            print(f"  {lang}/{algo}/{size}: {msg}")
    else:
        print("All cells completed successfully.")
 
 
if __name__ == "__main__":
    main()