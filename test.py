"""
pilot_study.py  –  Carbon Footprint Benchmark  (build-up version)
Step 1: LHM sensor reading
Step 2: Program execution
Step 3: Full pilot loop (50 runs per cell, 3 warm-ups discarded)
"""

import csv
import random
from datetime import datetime
from pathlib import Path
import requests
import time 
import subprocess
import sys
import os


LHM_URL        = "http://172.22.1.29:8085/data.json"
BASE_DIR       = Path(r"C:\Users\Stemadmin\Desktop\Anuj Khadka\carbon_footprint\implementations")
RESULTS_DIR    = Path(r"C:\Users\Stemadmin\Desktop\Anuj Khadka\carbon_footprint\results")
BUILD_DIR    = BASE_DIR / "build"
 
WARM_UP_RUNS   = 5
PILOT_RUNS     = 50
INTER_RUN_SLEEP = 0.05   # seconds between iterations (within a cell)



LANGUAGES = ["c", "rust", "go", "java", "javascript", "python"]
ALGORITHMS = ["summation", "binary_search", "merge_sort", "bfs", "hash_table", "matrix_multiplication"]
SIZES      = ["small", "med", "large"]


# Java class name mapping: algo -> class prefix (PascalCase)
JAVA_CLASS = {
    "summation":            "Summation",
    "binary_search":        "BinarySearch",
    "merge_sort":           "MergeSort",
    "bfs":                  "BFS",
    "hash_table":           "HashTable",
    "matrix_multiplication":"MatrixMultiplication",
}
 
# Java size suffix mapping
JAVA_SIZE = {"small": "Small", "mid": "Mid", "large": "Large"}
 
def get_cmd(language: str, algorithm: str, size: str) -> list[str]:
    if language == "c":
        exe = BUILD_DIR / f"{algorithm}_{size}_c.exe"
        return [str(exe)]
 
    elif language == "rust":
        exe = BUILD_DIR / f"{algorithm}_{size}_rust.exe"
        return [str(exe)]
 
    elif language == "go":
        exe = BUILD_DIR / f"{algorithm}_{size}_go.exe"
        return [str(exe)]
 
    elif language == "java":
        class_name = f"{JAVA_CLASS[algorithm]}_{JAVA_SIZE[size]}"
        cp = str(BASE_DIR / "java" / algorithm)
        return ["java", "-cp", cp, class_name]
 
    elif language == "javascript":
        js_file = BASE_DIR / "javascript" / algorithm / f"{algorithm}_{size}.js"
        return ["node", str(js_file)]
 
    elif language == "python":
        py_file = BASE_DIR / "python" / algorithm / f"{algorithm}_{size}.py"
        return ["python", str(py_file)]
 
    raise ValueError(f"Unknown language: {language}")
 
 
# ── LHM ───────────────────────────────────────────────────────────────────────
 
def get_cpu_package_watts() -> float:
    data = requests.get(LHM_URL).json()
 
    def search(node):
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
        raise RuntimeError("CPU Package power sensor not found.")
    return watts
 
 
# ── Single iteration ──────────────────────────────────────────────────────────
 
def run_one_iteration(proc: subprocess.Popen) -> tuple[float, str]:
    w_before = get_cpu_package_watts()
    t_before = time.perf_counter()
 
    proc.stdin.write("\n")
    proc.stdin.flush()
 
    checksum = proc.stdout.readline().strip()
 
    t_after  = time.perf_counter()
    w_after  = get_cpu_package_watts()
 
    elapsed       = t_after - t_before
    energy_joules = ((w_before + w_after) / 2) * elapsed
    return energy_joules, checksum
 
 
# ── One cell ──────────────────────────────────────────────────────────────────
 
def run_cell(language: str, algorithm: str, size: str) -> list[dict]:
    cmd = get_cmd(language, algorithm, size)
    print(f"  Launching: {' '.join(cmd)}")
 
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
 
    ready = proc.stdout.readline().strip()
    if ready != "ready":
        stderr_out = proc.stderr.read()
        proc.terminate()
        raise RuntimeError(
            f"Expected 'ready', got '{ready!r}'"
            + (f"\n    stderr: {stderr_out.strip()}" if stderr_out.strip() else "")
        )
 
    # Warm-up runs (discarded)
    for _ in range(WARM_UP_RUNS):
        run_one_iteration(proc)
        time.sleep(INTER_RUN_SLEEP)
 
    # Measured runs
    results = []
    for run_idx in range(1, PILOT_RUNS + 1):
        joules, checksum = run_one_iteration(proc)
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
    proc.wait()
    return results
 
 
# ── Main pilot loop ───────────────────────────────────────────────────────────
 
def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp   = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = RESULTS_DIR / f"pilot_{timestamp}.csv"
 
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