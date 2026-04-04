"""
pilot_study.py
--------------
Runs 50 iterations per (language, algorithm, size) combination and records
energy (J) from LibreHardwareMonitor RAPL + carbon intensity from Electricity Maps.

Purpose:
  - Measure per-cell variance so we can run a power analysis (see power_analysis.py)
    before committing to the full experiment.
  - Validate that all 36 implementations produce correct output (compared to C
    reference stdout captured here).
  - Detect outliers / warm-up effects so we can decide whether to discard first N runs.

Output files (written to ./pilot_output/):
  pilot_results.jsonl   - one JSON record per run (raw)
  pilot_summary.csv     - per-cell mean, std, cv, n
  pilot_report.txt      - human-readable summary for your methods section

Usage (run as Administrator so LHM driver is accessible):
  python pilot_study.py

  Optional flags:
    --runs 50          number of runs per cell (default 50)
    --lang c rust      restrict to specific languages
    --algo summation   restrict to specific algorithms
    --size small       restrict to specific sizes
    --skip-verify      skip output correctness check (not recommended)
"""

import argparse
import csv
import json
import os
import subprocess
import sys
import time
import statistics
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration — edit paths to match your machine
# ---------------------------------------------------------------------------

PROJECT_DIR = Path(r"C:\Users\AKhadka2\Desktop\carbon_footprint\implementations")

# Where compiled binaries will be placed
BUILD_DIR = PROJECT_DIR / "build"

# Electricity Maps API
ELECTRICITY_MAPS_API_KEY = "zyjqZja8pJXqecWbs6d2"   
ELECTRICITY_MAPS_ZONE    = "US-NY-NYIS"

# LibreHardwareMonitor REST endpoint
LHM_URL = "http://localhost:8085/data.json"

# Output directory for this pilot
OUT_DIR = PROJECT_DIR / "pilot_output"

# ---------------------------------------------------------------------------
# Experiment design
# ---------------------------------------------------------------------------

LANGUAGES = ["c", "rust", "go", "java", "javascript", "python"]

ALGORITHMS = [
    "summation",
    "binary_search",
    "merge_sort",
    "bfs",
    "hash_table",
    "matrix_multiplication",
]

SIZES = ["small", "medium", "large"]

# How to build and run each language.
# {algo}, {size}, {build_dir} are substituted at runtime.
# "build" is None for interpreted languages (no compile step).
LANG_CONFIG = {
    "c": {
        "build": "gcc -O2 -o {build_dir}\\{algo}_c.exe {project_dir}\\c\\{algo}.c",
        "run":   "{build_dir}\\{algo}_c.exe {size}",
        "ext":   ".c",
    },
    "rust": {
        "build": "cargo build --release --manifest-path {project_dir}\\rust\\{algo}\\Cargo.toml",
        "run":   "{project_dir}\\rust\\{algo}\\target\\release\\{algo}.exe {size}",
        "ext":   None,
    },
    "go": {
        "build": "go build -o {build_dir}\\{algo}_go.exe {project_dir}\\go\\{algo}.go",
        "run":   "{build_dir}\\{algo}_go.exe {size}",
        "ext":   ".go",
    },
    "java": {
        "build": "javac -d {build_dir} {project_dir}\\java\\{algo}.java",
        # Java main class name assumed to be TitleCase of algo (e.g. MergeSort)
        "run":   "java -cp {build_dir} {main_class} {size}",
        "ext":   ".java",
    },
    "javascript": {
        "build": None,
        "run":   "node {project_dir}\\javascript\\{algo}.js {size}",
        "ext":   ".js",
    },
    "python": {
        "build": None,
        "run":   "python {project_dir}\\python\\{algo}.py {size}",
        "ext":   ".py",
    },
}

def java_main_class(algo: str) -> str:
    """Convert algo name to expected Java class name, e.g. merge_sort -> MergeSort"""
    if algo == "bfs":
        return "BFS"
    return "".join(word.capitalize() for word in algo.split("_"))


def fmt(template: str, lang: str, algo: str, size: str) -> str:
    return template.format(
        project_dir = str(PROJECT_DIR),
        build_dir   = str(BUILD_DIR),
        algo        = algo,
        size        = size,
        main_class  = java_main_class(algo),
    )


def build_implementation(lang: str, algo: str) -> bool:
    """Compile if needed. Returns True on success."""
    cfg = LANG_CONFIG[lang]
    if cfg["build"] is None:
        return True   # interpreted — nothing to build

    cmd = fmt(cfg["build"], lang, algo, "")
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=60
        )
        if result.returncode != 0:
            print(f"  [BUILD FAIL] {lang}/{algo}\n  {result.stderr.strip()}")
            return False
        return True
    except subprocess.TimeoutExpired:
        print(f"  [BUILD TIMEOUT] {lang}/{algo}")
        return False


def run_once(lang: str, algo: str, size: str) -> dict | None:
    """
    Execute the implementation once, capturing stdout, wall time, and
    RAPL energy (Package) from LHM.

    Returns a dict with keys: stdout, wall_s, energy_j, error
    Returns None if the process failed.
    """
    cmd = fmt(LANG_CONFIG[lang]["run"], lang, algo, size)

    # Snapshot RAPL before
    energy_before = read_rapl_package_joules()

    t_start = time.perf_counter()
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=120
        )
    except subprocess.TimeoutExpired:
        return {"error": "timeout", "stdout": "", "wall_s": None, "energy_j": None}
    t_end = time.perf_counter()

    # Snapshot RAPL after
    energy_after = read_rapl_package_joules()

    if result.returncode != 0:
        return {
            "error": f"exit {result.returncode}: {result.stderr.strip()[:200]}",
            "stdout": "",
            "wall_s": None,
            "energy_j": None,
        }

    energy_j = None
    if energy_before is not None and energy_after is not None:
        energy_j = energy_after - energy_before
        # Guard against RAPL counter wrap or tiny negative due to timing jitter
        if energy_j < 0:
            energy_j = None

    return {
        "error":    None,
        "stdout":   result.stdout.strip(),
        "wall_s":   round(t_end - t_start, 6),
        "energy_j": round(energy_j, 4) if energy_j is not None else None,
    }


# ---------------------------------------------------------------------------
# LibreHardwareMonitor RAPL reader
# ---------------------------------------------------------------------------

_LHM_WARNED = False

def read_rapl_package_joules() -> float | None:
    """
    Fetch current CPU Package power reading from LHM REST API.

    LHM exposes a JSON tree. We walk it looking for a sensor whose
    Name contains 'Package' and Type == 'Energy' (unit: J).
    Falls back to Type == 'Power' (W) and returns watts (caller handles).
    """
    global _LHM_WARNED
    try:
        with urllib.request.urlopen(LHM_URL, timeout=2) as resp:
            data = json.loads(resp.read())
        return _extract_package_energy(data)
    except Exception as e:
        if not _LHM_WARNED:
            print(f"  [LHM WARNING] Cannot read RAPL: {e}")
            print("  Energy readings will be NULL. Check LHM is running as admin.")
            _LHM_WARNED = True
        return None


def _extract_package_energy(node: dict) -> float | None:
    """Recursively search LHM JSON tree for CPU Package Energy sensor (Joules)."""
    # LHM tree structure: {"Children": [...], "Text": "...", "Value": "...", "Type": "..."}
    if isinstance(node, dict):
        name  = node.get("Text", "")
        stype = node.get("Type", "")
        value = node.get("Value", "")
        # Look for energy sensor on the CPU package
        if "Package" in name and stype == "Energy":
            try:
                # Value looks like "1234.56 J" or "1 234,56 J"
                numeric = value.replace("\u00a0", "").replace(",", ".").split()[0]
                return float(numeric)
            except (ValueError, IndexError):
                pass
        for child in node.get("Children", []):
            result = _extract_package_energy(child)
            if result is not None:
                return result
    return None


# ---------------------------------------------------------------------------
# Electricity Maps carbon intensity
# ---------------------------------------------------------------------------

_carbon_intensity_cache: dict[str, float] = {}

def get_carbon_intensity() -> float | None:
    """
    Returns gCO2eq/kWh for the configured zone.
    Cached for the session — carbon intensity changes slowly (hourly).
    Call once at the start; the value is attached to every record.
    """
    cache_key = ELECTRICITY_MAPS_ZONE
    if cache_key in _carbon_intensity_cache:
        return _carbon_intensity_cache[cache_key]

    url = f"https://api.electricitymap.org/v3/carbon-intensity/latest?zone={ELECTRICITY_MAPS_ZONE}"
    req = urllib.request.Request(url, headers={"auth-token": ELECTRICITY_MAPS_API_KEY})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        ci = data.get("carbonIntensity")
        if ci is not None:
            _carbon_intensity_cache[cache_key] = float(ci)
            return float(ci)
    except Exception as e:
        print(f"  [ELEC MAPS WARNING] {e}")
    return None


def joules_to_gco2e(joules: float, ci: float) -> float:
    """Convert energy in Joules + carbon intensity (gCO2e/kWh) to gCO2e."""
    kwh = joules / 3_600_000
    return kwh * ci


# ---------------------------------------------------------------------------
# Output correctness verification
# ---------------------------------------------------------------------------

def build_reference_outputs(sizes: list[str]) -> dict[tuple, str]:
    """
    Run C implementation once per (algo, size) to capture reference stdout.
    Must be called after C binaries are built.
    """
    refs = {}
    print("\nCapturing C reference outputs...")
    for algo in ALGORITHMS:
        for size in sizes:
            result = run_once("c", algo, size)
            if result and result["error"] is None:
                refs[(algo, size)] = result["stdout"]
                print(f" c/{algo}/{size}")
            else:
                print(f" c/{algo}/{size} — {result}")
    return refs


# ---------------------------------------------------------------------------
# Main pilot loop
# ---------------------------------------------------------------------------

def run_pilot(
    n_runs:       int,
    languages:    list[str],
    algorithms:   list[str],
    sizes:        list[str],
    skip_verify:  bool,
) -> None:

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    BUILD_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    jsonl_path  = OUT_DIR / f"pilot_results_{timestamp}.jsonl"
    csv_path    = OUT_DIR / f"pilot_summary_{timestamp}.csv"
    report_path = OUT_DIR / f"pilot_report_{timestamp}.txt"

    print("=" * 60)
    print("CARBON FOOTPRINT PILOT STUDY")
    print(f"Started : {timestamp}")
    print(f"Runs/cell: {n_runs}")
    print(f"Languages: {languages}")
    print(f"Algorithms: {algorithms}")
    print(f"Sizes: {sizes}")
    print("=" * 60)

    # --- Fetch carbon intensity once ---
    print("\nFetching carbon intensity from Electricity Maps...")
    carbon_intensity = get_carbon_intensity()
    if carbon_intensity is not None:
        print(f"  Carbon intensity: {carbon_intensity} gCO2e/kWh (zone: {ELECTRICITY_MAPS_ZONE})")
    else:
        print("  [WARNING] Carbon intensity unavailable — gCO2e will be null in output")

    # --- Build all implementations ---
    print("\nBuilding compiled languages...")
    build_ok: set[tuple] = set()
    for lang in languages:
        for algo in algorithms:
            if lang == "rust":
                src_file = PROJECT_DIR / "rust" / algo / "src" / "main.rs"
            else:
                src_ext = LANG_CONFIG[lang]["ext"]
                lang_dir = PROJECT_DIR / lang
                src_file = lang_dir / f"{algo}{src_ext}"
            if not src_file.exists():
                print(f"  [SKIP] {lang}/{algo} — source not found at {src_file}")
                continue
            if build_implementation(lang, algo):
                build_ok.add((lang, algo))
                print(f" built {lang}/{algo}")
            else:
                print(f" failed {lang}/{algo}")

    # Mark interpreted languages as always "built"
    for lang in ["javascript", "python"]:
        if lang in languages:
            for algo in algorithms:
                src_ext = LANG_CONFIG[lang]["ext"]
                src_file = PROJECT_DIR / lang / f"{algo}{src_ext}"
                if src_file.exists():
                    build_ok.add((lang, algo))

    # --- Reference outputs ---
    reference_outputs: dict[tuple, str] = {}
    if not skip_verify and "c" in languages:
        reference_outputs = build_reference_outputs(sizes)

    # --- Pilot runs ---
    # Accumulate energy_j values per cell for summary statistics
    cell_data: dict[tuple, list[float]] = {}   # key: (lang, algo, size)
    cell_wall:  dict[tuple, list[float]] = {}
    cell_errors: dict[tuple, int] = {}

    total_cells = len([
        (l, a, s)
        for l in languages for a in algorithms for s in sizes
        if (l, a) in build_ok
    ])
    total_runs = total_cells * n_runs
    run_count  = 0

    print(f"\nStarting pilot runs ({total_cells} cells × {n_runs} runs = {total_runs} total)...")
    print("-" * 60)

    with open(jsonl_path, "w", encoding="utf-8") as jf:
        for lang in languages:
            for algo in algorithms:
                if (lang, algo) not in build_ok:
                    continue
                for size in sizes:
                    cell_key = (lang, algo, size)
                    cell_data[cell_key]   = []
                    cell_wall[cell_key]   = []
                    cell_errors[cell_key] = 0

                    ref_stdout = reference_outputs.get((algo, size))

                    for run_i in range(1, n_runs + 1):
                        run_count += 1
                        pct = 100 * run_count / total_runs
                        print(
                            f"  [{pct:5.1f}%] {lang:12s} {algo:15s} {size:8s} run {run_i:3d}/{n_runs}",
                            end="\r",
                        )

                        result = run_once(lang, algo, size)

                        # Correctness check
                        output_match = None
                        if ref_stdout is not None and result and result["stdout"]:
                            output_match = (result["stdout"] == ref_stdout)

                        # gCO2e
                        gco2e = None
                        if result and result["energy_j"] is not None and carbon_intensity is not None:
                            gco2e = round(joules_to_gco2e(result["energy_j"], carbon_intensity), 8)

                        record = {
                            "timestamp":        datetime.now(timezone.utc).isoformat(),
                            "run_index":        run_i,
                            "language":         lang,
                            "algorithm":        algo,
                            "size":             size,
                            "wall_s":           result["wall_s"]   if result else None,
                            "energy_j":         result["energy_j"] if result else None,
                            "gco2e":            gco2e,
                            "carbon_intensity": carbon_intensity,
                            "output_correct":   output_match,
                            "error":            result["error"]    if result else "run_failed",
                        }
                        jf.write(json.dumps(record) + "\n")

                        # Accumulate for stats (only successful runs with energy readings)
                        if result and result["error"] is None:
                            if result["energy_j"] is not None:
                                cell_data[cell_key].append(result["energy_j"])
                            if result["wall_s"] is not None:
                                cell_wall[cell_key].append(result["wall_s"])
                        else:
                            cell_errors[cell_key] += 1

                    # Print cell summary line
                    energies = cell_data[cell_key]
                    if energies:
                        mean_e = statistics.mean(energies)
                        std_e  = statistics.stdev(energies) if len(energies) > 1 else 0.0
                        cv     = (std_e / mean_e * 100) if mean_e > 0 else 0.0
                        print(
                            f"  DONE  {lang:12s} {algo:15s} {size:8s} "
                            f"mean={mean_e:.4f}J  std={std_e:.4f}J  CV={cv:.1f}%  "
                            f"errors={cell_errors[cell_key]}"
                        )
                    else:
                        print(
                            f"  DONE  {lang:12s} {algo:15s} {size:8s} "
                            f"NO ENERGY DATA  errors={cell_errors[cell_key]}"
                        )

    print("\nAll runs complete.")

    # --- Write CSV summary ---
    write_summary_csv(csv_path, cell_data, cell_wall, cell_errors, n_runs)

    # --- Write text report ---
    write_text_report(report_path, cell_data, cell_wall, cell_errors, n_runs, carbon_intensity, timestamp)

    print(f"\nOutput files:")
    print(f"  Raw JSONL : {jsonl_path}")
    print(f"  CSV       : {csv_path}")
    print(f"  Report    : {report_path}")


def write_summary_csv(
    path: Path,
    cell_data:   dict,
    cell_wall:   dict,
    cell_errors: dict,
    n_runs: int,
) -> None:
    rows = []
    for (lang, algo, size), energies in sorted(cell_data.items()):
        walls = cell_wall.get((lang, algo, size), [])
        n_ok  = len(energies)
        n_err = cell_errors.get((lang, algo, size), 0)

        mean_e = statistics.mean(energies)          if n_ok > 0 else None
        std_e  = statistics.stdev(energies)         if n_ok > 1 else None
        cv_e   = (std_e / mean_e * 100)             if (mean_e and std_e) else None
        min_e  = min(energies)                       if n_ok > 0 else None
        max_e  = max(energies)                       if n_ok > 0 else None
        mean_w = statistics.mean(walls)             if walls else None
        std_w  = statistics.stdev(walls)            if len(walls) > 1 else None

        rows.append({
            "language":       lang,
            "algorithm":      algo,
            "size":           size,
            "n_successful":   n_ok,
            "n_errors":       n_err,
            "n_total":        n_runs,
            "mean_energy_j":  round(mean_e, 6) if mean_e is not None else "",
            "std_energy_j":   round(std_e,  6) if std_e  is not None else "",
            "cv_pct":         round(cv_e,   2) if cv_e   is not None else "",
            "min_energy_j":   round(min_e,  6) if min_e  is not None else "",
            "max_energy_j":   round(max_e,  6) if max_e  is not None else "",
            "mean_wall_s":    round(mean_w, 6) if mean_w is not None else "",
            "std_wall_s":     round(std_w,  6) if std_w  is not None else "",
        })

    fieldnames = list(rows[0].keys()) if rows else []
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nCSV summary written: {path}")


def write_text_report(
    path: Path,
    cell_data:   dict,
    cell_wall:   dict,
    cell_errors: dict,
    n_runs: int,
    carbon_intensity: float | None,
    timestamp: str,
) -> None:
    lines = []
    lines.append("PILOT STUDY REPORT")
    lines.append("=" * 60)
    lines.append(f"Generated : {timestamp}")
    lines.append(f"Runs/cell : {n_runs}")
    lines.append(f"Carbon intensity: {carbon_intensity} gCO2e/kWh ({ELECTRICITY_MAPS_ZONE})")
    lines.append("")

    lines.append("COEFFICIENT OF VARIATION (CV%) BY CELL")
    lines.append("(CV% = std/mean * 100 — lower is more stable)")
    lines.append("-" * 60)

    high_cv_cells = []
    for (lang, algo, size), energies in sorted(cell_data.items()):
        n_ok = len(energies)
        if n_ok < 2:
            cv = None
        else:
            mean_e = statistics.mean(energies)
            std_e  = statistics.stdev(energies)
            cv     = (std_e / mean_e * 100) if mean_e > 0 else 0.0
        cv_str = f"{cv:.1f}%" if cv is not None else "N/A"
        flag   = " ← HIGH VARIANCE" if (cv is not None and cv > 10) else ""
        lines.append(f"  {lang:12s} {algo:15s} {size:8s}  CV={cv_str}{flag}")
        if cv is not None and cv > 10:
            high_cv_cells.append((lang, algo, size, cv))

    lines.append("")
    if high_cv_cells:
        lines.append("HIGH VARIANCE CELLS (CV > 10%) — consider more runs or investigation:")
        for lang, algo, size, cv in sorted(high_cv_cells, key=lambda x: -x[3]):
            lines.append(f"  {lang:12s} {algo:15s} {size:8s}  CV={cv:.1f}%")
    else:
        lines.append("All cells have CV <= 10% — variance looks stable.")

    lines.append("")
    lines.append("RECOMMENDED NEXT STEPS")
    lines.append("-" * 60)
    lines.append("1. Run power_analysis.py with this pilot CSV to determine N for full experiment.")
    lines.append("2. If any CV > 20%, investigate that cell before full experiment.")
    lines.append("3. Check 'output_correct' field in JSONL — all should be true or null.")
    lines.append("")
    lines.append("ERROR SUMMARY")
    lines.append("-" * 60)
    total_errors = sum(cell_errors.values())
    if total_errors == 0:
        lines.append("  No errors.")
    else:
        for (lang, algo, size), n_err in sorted(cell_errors.items()):
            if n_err > 0:
                lines.append(f"  {lang:12s} {algo:15s} {size:8s}  errors={n_err}/{n_runs}")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"Text report written: {path}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args():
    p = argparse.ArgumentParser(description="Carbon footprint pilot study")
    p.add_argument("--runs",        type=int,   default=50,          help="Runs per cell (default 50)")
    p.add_argument("--lang",        nargs="+",  default=LANGUAGES,   help="Languages to include")
    p.add_argument("--algo",        nargs="+",  default=ALGORITHMS,  help="Algorithms to include")
    p.add_argument("--size",        nargs="+",  default=SIZES,       help="Sizes to include")
    p.add_argument("--skip-verify", action="store_true",             help="Skip output correctness check")
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()

    # Validate
    bad_lang = [l for l in args.lang if l not in LANGUAGES]
    bad_algo = [a for a in args.algo if a not in ALGORITHMS]
    bad_size = [s for s in args.size if s not in SIZES]
    if bad_lang: sys.exit(f"Unknown languages: {bad_lang}. Valid: {LANGUAGES}")
    if bad_algo: sys.exit(f"Unknown algorithms: {bad_algo}. Valid: {ALGORITHMS}")
    if bad_size: sys.exit(f"Unknown sizes: {bad_size}. Valid: {SIZES}")

    run_pilot(
        n_runs      = args.runs,
        languages   = args.lang,
        algorithms  = args.algo,
        sizes       = args.size,
        skip_verify = args.skip_verify,
    )