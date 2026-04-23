"""
pilot_study.py  –  Carbon Footprint Benchmark  (build-up version)
Step 1: LHM sensor reading
Step 2: Program execution
Step 3: Full pilot loop (50 runs per cell, 5 warm-ups discarded)
"""

import csv
import random
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


COMMANDS = {
    "c":          lambda algo, size: [str(BASE_DIR / "c"          / algo / f"{algo}_{size}.exe")],
    "rust":       lambda algo, size: [str(BASE_DIR / "rust"       / algo / "target" / "release" / f"{algo}_{size}.exe")],
    "go":         lambda algo, size: [str(BASE_DIR / "go"         / algo / f"{algo}_{size}.exe")],
    "java":       lambda algo, size: ["java", "-cp", str(BASE_DIR / "java" / algo), f"{algo}_{size}"],
    "javascript": lambda algo, size: ["node", str(BASE_DIR / "javascript" / algo / f"{algo}_{size}.js")],
    "python":     lambda algo, size: ["python", str(BASE_DIR / "python"   / algo / f"{algo}_{size}.py")],
}


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

    t_before = time.perf_counter()
    w_before = get_cpu_package_watts()

    # Trigger the algorithm to run
    proc.stdin.write("\n")
    proc.stdin.flush()

    # Wait for the checksum line back
    checksum_line = proc.stdout.readline().strip()

    w_after = get_cpu_package_watts()
    t_after = time.perf_counter()

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
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
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