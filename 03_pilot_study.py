"""
pilot_study.py
--------------
Runs 50 measured iterations (+ 5 warm-up) per (algorithm, size) for C only.
Measures energy using LibreHardwareMonitor CPU Package power sensor.

Energy formula:
    energy_j = avg(watts_before, watts_after) * elapsed_seconds

Outputs:
    experiments/pilot/pilot_raw.csv       -- one row per measured run
    experiments/pilot/pilot_summary.json  -- variance summary per cell
    experiments/pilot/pilot_report.txt    -- recommended N + summary table

Usage (run as Administrator):
    python pilot_study.py

LHM must be running with web server enabled at http://172.22.1.29:8085
"""

import subprocess
import os
import sys
import time
import json
import csv
import math
import urllib.request

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

LHM_URL        = "http://172.22.1.29:8085/data.json"
SENSOR_ID      = "/intelcpu/0/power/0"   # CPU Package power (Watts)

ROOT           = os.path.dirname(os.path.abspath(__file__))
IMPL_DIR       = os.path.join(ROOT, "implementations")
BIN_DIR        = os.path.join(IMPL_DIR, "build")
OUT_DIR        = os.path.join(ROOT, "experiments", "pilot")

WARM_UP_RUNS   = 5
MEASURED_RUNS  = 50
TOTAL_RUNS     = WARM_UP_RUNS + MEASURED_RUNS

# Statistical parameters for power analysis
TARGET_POWER   = 0.80
ALPHA          = 0.05 / 15   # Bonferroni-corrected across 15 pairwise comparisons

ALGORITHMS = [
    "summation",
    "binary_search",
    "merge_sort",
    "bfs",
    "hash_table",
    "matrix_multiplication",
]

SIZES = ["small", "mid", "large"]


# ---------------------------------------------------------------------------
# LHM sensor reading
# ---------------------------------------------------------------------------

def read_watts():
    """Read CPU Package power (Watts) from LHM. Returns float or None."""
    try:
        with urllib.request.urlopen(LHM_URL, timeout=3) as resp:
            data = json.loads(resp.read().decode())
        return find_sensor(data, SENSOR_ID)
    except Exception as e:
        print(f"  [LHM ERROR] {e}")
        return None


def find_sensor(node, target_id):
    """Recursively search sensor tree for target SensorId. Returns float value."""
    if node.get("SensorId") == target_id:
        raw = node.get("RawValue", "")
        # RawValue is like "37.5 W" — strip unit
        try:
            return float(raw.split()[0])
        except Exception:
            return None
    for child in node.get("Children", []):
        result = find_sensor(child, target_id)
        if result is not None:
            return result
    return None


# ---------------------------------------------------------------------------
# Program execution
# ---------------------------------------------------------------------------

def get_exe(algo, size):
    return os.path.join(BIN_DIR, f"{algo}_{size}_c.exe")


def run_once(exe):
    """
    Launch program, wait for 'ready', sample watts_before,
    send trigger, run algorithm, sample watts_after, read checksum.
    Returns (energy_j, elapsed_s, watts_before, watts_after, checksum, error).
    """
    proc = None
    try:
        proc = subprocess.Popen(
            [exe],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # Wait for ready
        ready_line = proc.stdout.readline()
        if ready_line.strip() != "ready":
            proc.kill()
            proc.wait()
            return None, None, None, None, None, f"expected 'ready', got: {ready_line.strip()!r}"

        # Sample watts before trigger
        watts_before = read_watts()

        # Arm timer, send trigger, close stdin
        t0 = time.perf_counter()
        proc.stdin.write("\n")
        proc.stdin.flush()
        proc.stdin.close()

        # Read checksum
        checksum_line = proc.stdout.readline()
        elapsed_s = time.perf_counter() - t0

        # Sample watts after
        watts_after = read_watts()

        proc.wait(timeout=30)

        # Compute energy
        if watts_before is not None and watts_after is not None:
            avg_watts = (watts_before + watts_after) / 2.0
            energy_j  = avg_watts * elapsed_s
        else:
            energy_j = None

        return energy_j, elapsed_s, watts_before, watts_after, checksum_line.strip(), None

    except Exception as e:
        if proc:
            proc.kill()
            proc.wait()
        return None, None, None, None, None, str(e)


# ---------------------------------------------------------------------------
# Statistics helpers
# ---------------------------------------------------------------------------

def mean(values):
    return sum(values) / len(values)


def variance(values):
    m = mean(values)
    return sum((v - m) ** 2 for v in values) / (len(values) - 1)


def std(values):
    return math.sqrt(variance(values))


def compute_required_n(std_dev, alpha=ALPHA, power=TARGET_POWER):
    """
    Compute required N per group for Welch's t-test using normal approximation.
    Assumes equal variance and effect size = 1 std dev (Cohen's d = 1.0).
    Uses formula: N = 2 * ((z_alpha/2 + z_beta) / delta)^2 * sigma^2
    where delta = std_dev (effect size = 1 SD), z_alpha/2 and z_beta from
    standard normal.
    """
    # z-scores for alpha/2 (two-tailed) and power
    # alpha = 0.0033 → z ≈ 2.935
    # power = 0.80   → z ≈ 0.842
    z_alpha = _z_from_p(alpha / 2)
    z_beta  = 0.842  # z for power = 0.80

    if std_dev == 0:
        return 2  # degenerate case

    # Effect size: assume minimum detectable difference = 1 std dev
    delta = std_dev
    n = 2 * ((z_alpha + z_beta) / delta) ** 2 * (std_dev ** 2)
    return max(2, math.ceil(n))


def _z_from_p(p):
    """Approximate inverse normal CDF using rational approximation."""
    # Abramowitz and Stegun approximation
    t = math.sqrt(-2 * math.log(p))
    c = [2.515517, 0.802853, 0.010328]
    d = [1.432788, 0.189269, 0.001308]
    return t - (c[0] + c[1]*t + c[2]*t**2) / (1 + d[0]*t + d[1]*t**2 + d[2]*t**3)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    # Verify LHM is reachable
    print("Checking LHM connection...")
    test_watts = read_watts()
    if test_watts is None:
        print(f"ERROR: Cannot read from LHM at {LHM_URL}")
        print("Make sure LHM is running with web server enabled (run as Administrator).")
        sys.exit(1)
    print(f"LHM OK — CPU Package: {test_watts:.1f} W\n")

    raw_csv_path     = os.path.join(OUT_DIR, "pilot_raw.csv")
    summary_json_path= os.path.join(OUT_DIR, "pilot_summary.json")
    report_txt_path  = os.path.join(OUT_DIR, "pilot_report.txt")

    raw_rows  = []   # for CSV
    summary   = {}   # for JSON
    max_n     = 2    # track recommended N across all cells

    total_cells = len(ALGORITHMS) * len(SIZES)
    cell_num    = 0

    print("=" * 70)
    print("  PILOT STUDY — C language")
    print(f"  {WARM_UP_RUNS} warm-up + {MEASURED_RUNS} measured runs per cell")
    print(f"  {total_cells} cells total")
    print("=" * 70)

    for algo in ALGORITHMS:
        for size in SIZES:
            cell_num += 1
            exe = get_exe(algo, size)

            if not os.path.exists(exe):
                print(f"\n[{cell_num}/{total_cells}] SKIP {algo}_{size} — binary not found: {exe}")
                continue

            print(f"\n[{cell_num}/{total_cells}] {algo} / {size}")

            energy_readings = []
            errors          = 0

            for run_idx in range(TOTAL_RUNS):
                is_warmup = run_idx < WARM_UP_RUNS
                label     = f"  warm-up {run_idx + 1}" if is_warmup else f"  run {run_idx - WARM_UP_RUNS + 1:>2}"

                energy_j, elapsed_s, w_before, w_after, checksum, err = run_once(exe)

                if err:
                    print(f"{label}  ERROR: {err}")
                    errors += 1
                    continue

                if energy_j is None:
                    print(f"{label}  WARN: could not read LHM")
                    errors += 1
                    continue

                status = "warm-up" if is_warmup else "measured"

                print(f"{label}  {energy_j*1000:.4f} mJ  "
                      f"({elapsed_s*1000:.2f}ms)  "
                      f"[{w_before:.1f}W → {w_after:.1f}W]")

                if not is_warmup:
                    energy_readings.append(energy_j)
                    raw_rows.append({
                        "language":  "c",
                        "algorithm": algo,
                        "size":      size,
                        "run_index": run_idx - WARM_UP_RUNS,
                        "energy_j":  energy_j,
                        "elapsed_s": elapsed_s,
                        "watts_before": w_before,
                        "watts_after":  w_after,
                        "checksum":  checksum,
                    })

            # Per-cell summary
            if len(energy_readings) >= 2:
                m    = mean(energy_readings)
                s    = std(energy_readings)
                cv   = (s / m * 100) if m > 0 else 0
                n    = compute_required_n(s)
                max_n = max(max_n, n)

                summary[f"c_{algo}_{size}"] = {
                    "language":   "c",
                    "algorithm":  algo,
                    "size":       size,
                    "n_measured": len(energy_readings),
                    "mean_j":     m,
                    "std_j":      s,
                    "cv_pct":     cv,
                    "recommended_n": n,
                    "errors":     errors,
                }

                print(f"  → mean={m*1000:.4f}mJ  std={s*1000:.4f}mJ  "
                      f"CV={cv:.1f}%  recommended_N={n}")
            else:
                print(f"  → insufficient data ({len(energy_readings)} readings, {errors} errors)")

    # ---------------------------------------------------------------------------
    # Write outputs
    # ---------------------------------------------------------------------------

    # 1. Raw CSV
    if raw_rows:
        fieldnames = ["language", "algorithm", "size", "run_index",
                      "energy_j", "elapsed_s", "watts_before", "watts_after", "checksum"]
        with open(raw_csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(raw_rows)
        print(f"\nRaw CSV saved: {raw_csv_path}")

    # 2. Summary JSON
    with open(summary_json_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"Summary JSON saved: {summary_json_path}")

    # 3. Report TXT
    with open(report_txt_path, "w") as f:
        f.write("PILOT STUDY REPORT — C language\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Warm-up runs discarded : {WARM_UP_RUNS}\n")
        f.write(f"Measured runs per cell : {MEASURED_RUNS}\n")
        f.write(f"Target power           : {TARGET_POWER}\n")
        f.write(f"Alpha (Bonferroni)     : {ALPHA:.6f}  (0.05 / 15)\n\n")
        f.write(f"{'CELL':<40} {'MEAN(mJ)':>10} {'STD(mJ)':>10} "
                f"{'CV%':>6} {'REC_N':>6}\n")
        f.write("-" * 70 + "\n")

        for key, v in summary.items():
            cell = f"c / {v['algorithm']} / {v['size']}"
            f.write(f"{cell:<40} {v['mean_j']*1000:>10.4f} {v['std_j']*1000:>10.4f} "
                    f"{v['cv_pct']:>6.1f} {v['recommended_n']:>6}\n")

        f.write("\n" + "=" * 70 + "\n")
        f.write(f"RECOMMENDED N FOR MAIN EXPERIMENT: {max_n}\n")
        f.write("(Maximum across all cells — ensures sufficient power for worst case)\n")
        f.write("=" * 70 + "\n")

    print(f"Report saved: {report_txt_path}")

    # Terminal summary
    print("\n" + "=" * 70)
    print(f"  RECOMMENDED N FOR MAIN EXPERIMENT: {max_n}")
    print(f"  (Maximum recommended_n across all {len(summary)} cells)")
    print("=" * 70)


if __name__ == "__main__":
    main()