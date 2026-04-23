"""
benchmark_runner.py  –  Main Carbon Footprint Benchmark
- N = 115 runs per cell (power analysis result)
- 5 warm-up runs discarded per cell
- Randomized cell order
- Carbon intensity fetched from Electricity Maps every 30 minutes
- Saves: language, algorithm, size, run, joules, kwh, carbon_intensity, gco2e, checksum
"""
 
import csv
import random
import sys
import time
import subprocess
from datetime import datetime
from pathlib import Path
 
import requests
 


LHM_URL = "http://172.22.1.29:8085/data.json"
EM_ZONE = "US-NY-NYIS"
EMAP_API_KEY = "YTnrswWx69SezDhcrWpk"
EM_URL = f"https://api.electricitymaps.com/v3/carbon-intensity/latest?zone={EM_ZONE}"
CI_REFRESH_S  = 30 * 60   # refresh carbon intensity every 30 minutes


BASE_DIR      = Path(r"C:\Users\Stemadmin\Desktop\Anuj Khadka\carbon_footprint\implementations")
RESULTS_DIR   = Path(r"C:\Users\Stemadmin\Desktop\Anuj Khadka\carbon_footprint\results")
BUILD_DIR     = BASE_DIR / "build"

WARM_UP_RUNS  = 5
MAIN_RUNS     = 1
INTER_RUN_SLEEP = 0.05    # seconds between iterations within a cell
INTER_CELL_SLEEP = 5      # seconds between cells


response = requests.get(
    # "https://api.electricitymaps.com/v3/carbon-intensity/latest",
    EM_URL,
    headers={
        "auth-token": EMAP_API_KEY
    }
)
print(response.json())

def bold(s):  return f"\033[1m{s}\033[0m"
def green(s): return f"\033[92m{s}\033[0m"
def red(s):   return f"\033[91m{s}\033[0m"
def yellow(s):return f"\033[93m{s}\033[0m"




LANGUAGES  = ["c", "rust", "go", "java", "javascript", "python"]
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
    "java":       lambda algo, size: [
                      "java", "-Xss4m", "-cp", str(BASE_DIR / "java"),
                      f"{algo}.{JAVA_CLASS[algo]}_{JAVA_SIZE[size]}"
                  ],
    "javascript": lambda algo, size: ["node", str(BASE_DIR / "javascript" / algo / f"{algo}_{size}.js")],
    "python":     lambda algo, size: [sys.executable, str(BASE_DIR / "python" / algo / f"{algo}_{size}.py")],
}
 

###############################################################################################
########################## Carbon Intensity #####################

_ci_value = None
_ci_fetched_at = 0.0



def get_carbon_intensity() -> float:
    """
    Return carbon intensity (gCO2/kWh) for US-NY-NYIS.
    Refreshes from Electricity Maps API at most once every 30 minutes.
    """
    global _ci_value, _ci_fetched_at
    now = time.time()
    if _ci_value is None or (now - _ci_fetched_at) > CI_REFRESH_S:
        try:
            resp = requests.get(EM_URL, headers={"auth-token": EMAP_API_KEY}, timeout=10)
            resp.raise_for_status()
            _ci_value = float(resp.json()["carbonIntensity"])
            _ci_fetched_at = now
            print(f"  [Carbon intensity updated: {_ci_value:.1f} gCO2/kWh]")
        except Exception as e:
            if _ci_value is None:
                raise RuntimeError(f"Could not fetch carbon intensity: {e}")
            print(f"  [Carbon intensity refresh failed ({e}), reusing {_ci_value:.1f}]")
    return _ci_value
 


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





def run_cell(language: str, algorithm: str, size: str,
             carbon_intensity: float) -> list[dict]:
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
 
    ready = proc.stdout.readline().strip()
    if ready != "ready":
        stderr_out = proc.stderr.read()
        proc.terminate()
        msg = f"Expected 'ready', got '{ready!r}'"
        if stderr_out.strip():
            msg += f"\n    stderr: {stderr_out.strip()}"
        raise RuntimeError(msg)
 
    # Warm-up runs (discarded)
    for _ in range(WARM_UP_RUNS):
        run_once(proc)
        time.sleep(INTER_RUN_SLEEP)
 
    # Measured runs
    results = []
    for run_idx in range(1, MAIN_RUNS + 1):
        joules, checksum = run_once(proc)
        kwh    = joules / 3_600_000
        gco2e  = kwh * carbon_intensity
        results.append({
            "language":         language,
            "algorithm":        algorithm,
            "size":             size,
            "run":              run_idx,
            "joules":           joules,
            "kwh":              kwh,
            "carbon_intensity": carbon_intensity,
            "gco2e":            gco2e,
            "checksum":         checksum,
        })
        time.sleep(INTER_RUN_SLEEP)
 
    proc.stdin.close()
    try:
        proc.wait(timeout=30)
    except subprocess.TimeoutExpired:
        proc.kill()
        raise RuntimeError(f"Process did not exit within 30s")
    return results
 



def main():
    sys.stdout.reconfigure(line_buffering=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
 
    timestamp   = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = RESULTS_DIR / f"benchmark_{timestamp}.csv"
 
    cells = [
        (lang, algo, size)
        for lang in LANGUAGES
        for algo in ALGORITHMS
        for size in SIZES
    ]
    random.shuffle(cells)
 
    fieldnames = [
        "language", "algorithm", "size", "run",
        "joules", "kwh", "carbon_intensity", "gco2e", "checksum"
    ]
    errors = []
 
    # Fetch carbon intensity once at the start
    print("Fetching initial carbon intensity...")
    ci = get_carbon_intensity()
 
    with open(output_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
 
        total = len(cells)
        for idx, (lang, algo, size) in enumerate(cells, 1):
            print(f"\n[{idx}/{total}] {lang} / {algo} / {size}")
 
            # Refresh carbon intensity if needed
            ci = get_carbon_intensity()
 
            try:
                rows = run_cell(lang, algo, size, ci)
 
                checksums = {r["checksum"] for r in rows}
                if len(checksums) > 1:
                    print(f"  WARNING: inconsistent checksums: {checksums}")
                else:
                    print(f"  Checksum ✓  ({checksums.pop()})")
 
                writer.writerows(rows)
                f.flush()
 
                avg_mj    = sum(r["joules"] for r in rows) / len(rows) * 1000
                avg_gco2e = sum(r["gco2e"]  for r in rows) / len(rows)
                print(f"  Avg energy:  {avg_mj:.4f} mJ")
                print(f"  Avg gCO2e:   {avg_gco2e:.10f} g  (CI={ci:.1f} gCO2/kWh)")
 
            except Exception as e:
                print(f"  ERROR: {e}")
                errors.append((lang, algo, size, str(e)))
 
            time.sleep(INTER_CELL_SLEEP)
 
    print(f"\n{'='*60}")
    print(f"Benchmark complete. Results saved to:\n  {output_file}")
    if errors:
        print(f"\nFailed cells ({len(errors)}):")
        for lang, algo, size, msg in errors:
            print(f"  {lang}/{algo}/{size}: {msg}")
    else:
        print("All cells completed successfully.")
 
 
if __name__ == "__main__":
    main()