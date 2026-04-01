"""

Benchmark orchestration harness for the carbon footprint research project.

Responsibilities
----------------
1. WARM-UP  — discard initial runs to stabilise CPU caches and JIT compilers
2. TIMED RUNS — execute each (language × algorithm × size) N times
3. ENERGY LOGGING — read Intel RAPL via LibreHardwareMonitor HTTP API after each run
4. CARBON CONVERSION — call Electricity Maps API to get real-time gCO2/kWh for US-NY-NYIS
5. STRUCTURED LOGGING — write one JSON-Lines record per run to a rolling log file
6. SUMMARY REPORT — write a consolidated CSV + JSON report when all runs complete

Design principles
-----------------
- C is compiled once per session; all other languages compiled/interpreted as configured
- Warm-up runs are timed but their energy/carbon values are NOT recorded in the main log
- Each timed run is isolated: process spawned fresh, stdout captured and verified
- If RAPL or Electricity Maps is unavailable the run is still logged with null energy fields
  so the experiment can continue and energy data filled in later
- All timestamps in ISO-8601 UTC

Usage
-----
    python test_harness.py [OPTIONS]

Key options
-----------
    --impl-dir PATH         implementations/ root  (default: ./implementations)
    --log-dir  PATH         where logs go          (default: ./logs)
    --runs     N            timed runs per combo   (default: 30)
    --warmup   N            warm-up runs to discard(default: 5)
    --lhm-url  URL          LibreHardwareMonitor API base URL
                            (default: http://localhost:8085)
    --emap-key KEY          Electricity Maps API key (or set env EMAP_API_KEY)
    --algo     NAME         restrict to one algorithm
    --lang     NAME         restrict to one language
    --size     small|medium|large  restrict to one input size
    --dry-run               compile only, no timed runs (smoke test)
    --verbose               extra logging to stdout

Environment variables
---------------------
    EMAP_API_KEY   Electricity Maps API key
    LHM_URL        LibreHardwareMonitor base URL override
"""

from __future__ import annotations

import argparse
import csv
import datetime
import json
import logging
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
import urllib.error
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

# ─────────────────────────────────────────────────────────────────────────────
# Static configuration — edit here if your setup differs
# ─────────────────────────────────────────────────────────────────────────────

ALGORITHMS   = ["summation", "binary_search", "merge_sort", "bfs", "hash_table", "matrix_mul"]
INPUT_SIZES  = ["small", "medium", "large"]
LANGUAGES    = ["c", "rust", "go", "java", "javascript", "python"]
REFERENCE_LANG = "c"

JAVA_CLASS_NAMES = {
    "summation":     "Summation",
    "binary_search": "BinarySearch",
    "merge_sort":    "MergeSort",
    "bfs":           "BFS",
    "hash_table":    "HashTable",
    "matrix_mul":    "MatrixMul",
}

ON_WINDOWS   = platform.system() == "Windows"
TIMEOUT_SEC  = 120   # max wall-clock per individual run

# RAPL sensor name patterns (LibreHardwareMonitor uses these paths)
LHM_RAPL_PATHS = [
    "package",      # Package power (whole CPU)
    "cores",        # Core power only
]

EMAP_ZONE = "US-NY-NYIS"

# ─────────────────────────────────────────────────────────────────────────────
# Data classes
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class RunRecord:
    """One timed (non-warm-up) benchmark run — serialised to JSONL log."""
    session_id:        str
    run_index:         int       # 1-based within this combo
    language:          str
    algorithm:         str
    input_size:        str
    is_warmup:         bool

    # Timing
    start_utc:         str       # ISO-8601
    end_utc:           str
    wall_s:            float     # wall-clock seconds

    # Output verification
    output_matches_ref: Optional[bool]
    stdout_hash:       str       # SHA-256 hex of normalised stdout

    # Energy (filled in from RAPL if available)
    rapl_package_j:    Optional[float]  = None   # joules — package domain
    rapl_cores_j:      Optional[float]  = None   # joules — cores domain

    # Carbon
    carbon_intensity_gco2_kwh: Optional[float] = None
    energy_kwh:        Optional[float] = None
    carbon_gco2e:      Optional[float] = None

    # Process info
    returncode:        int  = 0
    stderr_snippet:    str  = ""    # first 200 chars of stderr
    error:             str  = ""    # harness-level error if any


@dataclass
class CompiledBinary:
    language:  str
    algorithm: str
    # For C / Rust: path to compiled binary
    # For Go: path to source (uses `go run`)
    # For Java: (classpath_dir, class_name)
    # For JS / Python: path to source
    exe_path:  Optional[str]       = None
    src_path:  Optional[str]       = None
    classpath: Optional[str]       = None
    classname: Optional[str]       = None
    error:     str                 = ""

# ─────────────────────────────────────────────────────────────────────────────
# Logging setup
# ─────────────────────────────────────────────────────────────────────────────

def setup_logging(log_dir: Path, verbose: bool, session_id: str) -> logging.Logger:
    log_dir.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("harness")
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    fmt = logging.Formatter("%(asctime)s  %(levelname)-7s  %(message)s",
                            datefmt="%H:%M:%S")

    # Console
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG if verbose else logging.INFO)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    # File (full DEBUG always)
    fh = logging.FileHandler(log_dir / f"harness_{session_id}.log", encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    return logger

# ─────────────────────────────────────────────────────────────────────────────
# Utility
# ─────────────────────────────────────────────────────────────────────────────

import hashlib

def sha256_of(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:16]

def normalise_output(raw: str) -> str:
    lines = [l.rstrip() for l in raw.splitlines()]
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines)

def utc_now() -> str:
    return datetime.datetime.utcnow().isoformat(timespec="milliseconds") + "Z"

def find_exe(name: str) -> Optional[str]:
    return shutil.which(name)

def run_subprocess(cmd: list[str], cwd: Optional[str] = None
                   ) -> tuple[int, str, str, float]:
    """Run command, return (rc, stdout, stderr, wall_seconds)."""
    t0 = time.perf_counter()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True,
                           timeout=TIMEOUT_SEC, cwd=cwd)
        return p.returncode, p.stdout, p.stderr, time.perf_counter() - t0
    except subprocess.TimeoutExpired:
        return -1, "", f"TIMEOUT>{TIMEOUT_SEC}s", time.perf_counter() - t0
    except Exception as exc:
        return -1, "", str(exc), time.perf_counter() - t0

# ─────────────────────────────────────────────────────────────────────────────
# Compiler / build step
# ─────────────────────────────────────────────────────────────────────────────

class Builder:
    def __init__(self, impl_dir: Path, tmp_dir: str, logger: logging.Logger):
        self.impl_dir = impl_dir
        self.tmp_dir  = tmp_dir
        self.log      = logger

    def _src(self, lang: str, algo: str) -> Optional[Path]:
        ext = {"c":"c","rust":"rs","go":"go","java":"java",
               "javascript":"js","python":"py"}[lang]
        fname = (JAVA_CLASS_NAMES[algo] if lang == "java" else algo) + "." + ext
        p = self.impl_dir / lang / fname
        return p if p.exists() else None

    def build(self, lang: str, algo: str) -> CompiledBinary:
        src = self._src(lang, algo)
        if src is None:
            return CompiledBinary(lang, algo,
                error=f"Source missing: {self.impl_dir}/{lang}/...")

        if lang == "c":
            return self._build_c(algo, src)
        elif lang == "rust":
            return self._build_rust(algo, src)
        elif lang == "go":
            # No explicit compile; use `go run` at run time
            return CompiledBinary(lang, algo, src_path=str(src))
        elif lang == "java":
            return self._build_java(algo, src)
        elif lang in ("javascript", "python"):
            return CompiledBinary(lang, algo, src_path=str(src))
        else:
            return CompiledBinary(lang, algo, error=f"Unknown language: {lang}")

    def _build_c(self, algo: str, src: Path) -> CompiledBinary:
        gcc = find_exe("gcc")
        if not gcc:
            return CompiledBinary("c", algo, error="gcc not found")
        exe = os.path.join(self.tmp_dir, f"c_{algo}" + (".exe" if ON_WINDOWS else ""))
        rc, _, err, _ = run_subprocess([gcc, str(src), "-O2", "-o", exe])
        if rc != 0:
            return CompiledBinary("c", algo, error=f"gcc compile failed:\n{err[:400]}")
        self.log.debug(f"  compiled c/{algo} → {exe}")
        return CompiledBinary("c", algo, exe_path=exe)

    def _build_rust(self, algo: str, src: Path) -> CompiledBinary:
        rustc = find_exe("rustc")
        if not rustc:
            return CompiledBinary("rust", algo, error="rustc not found")
        exe = os.path.join(self.tmp_dir,
                           f"rust_{algo}" + (".exe" if ON_WINDOWS else ""))
        rc, _, err, _ = run_subprocess(
            [rustc, str(src), "--edition", "2021", "-o", exe])
        if rc != 0:
            return CompiledBinary("rust", algo,
                                  error=f"rustc compile failed:\n{err[:400]}")
        self.log.debug(f"  compiled rust/{algo} → {exe}")
        return CompiledBinary("rust", algo, exe_path=exe)

    def _build_java(self, algo: str, src: Path) -> CompiledBinary:
        javac = find_exe("javac")
        if not javac:
            return CompiledBinary("java", algo, error="javac not found")
        cp = os.path.join(self.tmp_dir, f"java_{algo}")
        os.makedirs(cp, exist_ok=True)
        rc, _, err, _ = run_subprocess([javac, "-d", cp, str(src)])
        if rc != 0:
            return CompiledBinary("java", algo,
                                  error=f"javac compile failed:\n{err[:400]}")
        cn = JAVA_CLASS_NAMES[algo]
        self.log.debug(f"  compiled java/{algo} → {cp}/{cn}.class")
        return CompiledBinary("java", algo, classpath=cp, classname=cn)

# ─────────────────────────────────────────────────────────────────────────────
# Runner (execute one run of a compiled binary)
# ─────────────────────────────────────────────────────────────────────────────

class LangRunner:
    def __init__(self, logger: logging.Logger):
        self.log = logger

    def run(self, binary: CompiledBinary, size: str) -> tuple[int, str, str, float]:
        """Return (returncode, stdout, stderr, wall_s)."""
        lang = binary.language
        if lang == "c":
            return run_subprocess([binary.exe_path, size])
        elif lang == "rust":
            return run_subprocess([binary.exe_path, size])
        elif lang == "go":
            go = find_exe("go")
            if not go:
                return -1, "", "go not found", 0.0
            return run_subprocess([go, "run", binary.src_path, size])
        elif lang == "java":
            java = find_exe("java")
            if not java:
                return -1, "", "java not found", 0.0
            return run_subprocess(
                [java, "-server", "-cp", binary.classpath, binary.classname, size])
        elif lang == "javascript":
            node = find_exe("node")
            if not node:
                return -1, "", "node not found", 0.0
            return run_subprocess([node, binary.src_path, size])
        elif lang == "python":
            py = find_exe("python") or find_exe("python3")
            if not py:
                return -1, "", "python not found", 0.0
            return run_subprocess([py, binary.src_path, size])
        else:
            return -1, "", f"Unknown language: {lang}", 0.0

# ─────────────────────────────────────────────────────────────────────────────
# LibreHardwareMonitor RAPL reader
# ─────────────────────────────────────────────────────────────────────────────

class RAPLReader:
    """
    Reads CPU energy from LibreHardwareMonitor's built-in HTTP server.

    LHM exposes a JSON tree at GET /data.json  (default port 8085).
    We walk the tree looking for sensor nodes whose Text field contains
    "Package" or "Cores" and whose SensorType is "Power" (watts).

    Strategy: read watts BEFORE and AFTER the run, average them, multiply
    by wall-clock seconds to get joules.  This is an approximation but is
    standard for RAPL-via-LHM on Windows.

    For higher accuracy you would poll at ~100 ms intervals during the run;
    that complexity is left for Phase 3 if needed.
    """

    def __init__(self, base_url: str, logger: logging.Logger):
        self.base_url = base_url.rstrip("/")
        self.log      = logger
        self._available: Optional[bool] = None

    def _fetch(self) -> Optional[dict]:
        url = f"{self.base_url}/data.json"
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=3) as resp:
                return json.loads(resp.read().decode())
        except Exception as exc:
            self.log.debug(f"LHM fetch error: {exc}")
            return None

    def available(self) -> bool:
        if self._available is None:
            data = self._fetch()
            self._available = data is not None
            if self._available:
                self.log.info("LibreHardwareMonitor API reachable.")
            else:
                self.log.warning(
                    "LibreHardwareMonitor not reachable — energy will be NULL. "
                    "Start LHM and enable its Web Server (Options → Web Server).")
        return self._available

    def _walk(self, node: dict, results: dict):
        """Recursively walk LHM JSON tree, collect power sensor values."""
        text = node.get("Text", "")
        typ  = node.get("Type", "")
        val  = node.get("Value", "")

        if typ == "Sensor" and "Power" in node.get("SensorType", ""):
            key = text.lower()
            try:
                watts = float(val.replace(",", ".").split()[0])
            except Exception:
                watts = None
            if "package" in key:
                results["package_w"] = watts
            elif "core" in key:
                results["cores_w"] = watts

        for child in node.get("Children", []):
            self._walk(child, results)

    def read_watts(self) -> dict:
        """Return {'package_w': float|None, 'cores_w': float|None}."""
        data = self._fetch()
        if data is None:
            return {"package_w": None, "cores_w": None}
        result = {}
        self._walk(data, result)
        return {
            "package_w": result.get("package_w"),
            "cores_w":   result.get("cores_w"),
        }

    def measure_run(self, run_fn) -> tuple:
        """
        Call run_fn(), return (run_result, package_j, cores_j).
        Uses before/after watt reading × wall time as joule estimate.
        """
        if not self.available():
            result = run_fn()
            return result, None, None

        before = self.read_watts()
        result = run_fn()          # ← actual benchmark run happens here
        after  = self.read_watts()

        wall_s = result[3]  # run_subprocess returns (rc, out, err, wall_s)

        def joules(key):
            b = before.get(key)
            a = after.get(key)
            if b is None or a is None:
                return None
            return ((b + a) / 2.0) * wall_s

        return result, joules("package_w"), joules("cores_w")

# ─────────────────────────────────────────────────────────────────────────────
# Electricity Maps carbon intensity
# ─────────────────────────────────────────────────────────────────────────────

class CarbonIntensityClient:
    """Fetch real-time marginal carbon intensity from Electricity Maps API."""

    _ENDPOINT = "https://api.electricitymap.org/v3/carbon-intensity/latest"

    def __init__(self, api_key: str, zone: str, logger: logging.Logger):
        self.api_key  = api_key
        self.zone     = zone
        self.log      = logger
        self._cache: Optional[tuple[float, float]] = None  # (intensity, ts)
        self._cache_ttl = 300  # seconds — refresh at most every 5 min

    def get_intensity(self) -> Optional[float]:
        """Return gCO2/kWh or None on error."""
        if not self.api_key:
            self.log.debug("No Electricity Maps API key — carbon intensity will be NULL.")
            return None

        now = time.time()
        if self._cache and (now - self._cache[1]) < self._cache_ttl:
            return self._cache[0]

        url = f"{self._ENDPOINT}?zone={self.zone}"
        req = urllib.request.Request(
            url,
            headers={"auth-token": self.api_key, "Accept": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data  = json.loads(resp.read().decode())
                val   = float(data["carbonIntensity"])
                self._cache = (val, now)
                self.log.debug(f"Carbon intensity: {val} gCO2/kWh (zone={self.zone})")
                return val
        except Exception as exc:
            self.log.warning(f"Electricity Maps API error: {exc}")
            return None

# ─────────────────────────────────────────────────────────────────────────────
# JSONL run logger
# ─────────────────────────────────────────────────────────────────────────────

class RunLogger:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._fh = open(path, "a", encoding="utf-8")

    def write(self, record: RunRecord):
        self._fh.write(json.dumps(asdict(record)) + "\n")
        self._fh.flush()

    def close(self):
        self._fh.close()

# ─────────────────────────────────────────────────────────────────────────────
# Warm-up protocol
# ─────────────────────────────────────────────────────────────────────────────

def run_warmup(
    binary: CompiledBinary,
    size: str,
    n_warmup: int,
    runner: LangRunner,
    logger: logging.Logger,
):
    """
    Execute n_warmup runs that are NOT logged.
    Purpose:
      - C/Rust: warm OS file cache and branch predictor
      - Java:   trigger JIT compilation (server JVM needs ~10k iterations
                internally, but a few full runs prime the JVM class loader)
      - JS:     let V8 optimise hot paths
      - Python: warm module imports and bytecode cache (.pyc)
      - All:    stabilise CPU frequency (Intel Turbo Boost settles after
                first sustained load burst)
    """
    lang = binary.language
    logger.debug(f"  warm-up {lang}/{binary.algorithm}/{size} × {n_warmup}")
    for i in range(n_warmup):
        rc, out, err, wall = runner.run(binary, size)
        logger.debug(f"    warm-up run {i+1}: rc={rc}  wall={wall:.3f}s")
        if rc != 0:
            logger.warning(
                f"  Warm-up run {i+1} failed (rc={rc}): {err[:80]}")

# ─────────────────────────────────────────────────────────────────────────────
# Core orchestration
# ─────────────────────────────────────────────────────────────────────────────

class Harness:
    def __init__(
        self,
        impl_dir:    Path,
        log_dir:     Path,
        n_runs:      int,
        n_warmup:    int,
        lhm_url:     str,
        emap_key:    str,
        session_id:  str,
        logger:      logging.Logger,
        dry_run:     bool = False,
    ):
        self.impl_dir   = impl_dir
        self.log_dir    = log_dir
        self.n_runs     = n_runs
        self.n_warmup   = n_warmup
        self.dry_run    = dry_run
        self.session_id = session_id
        self.logger     = logger

        self._tmp      = tempfile.mkdtemp(prefix="harness_")
        self.builder   = Builder(impl_dir, self._tmp, logger)
        self.runner    = LangRunner(logger)
        self.rapl      = RAPLReader(lhm_url, logger)
        self.carbon    = CarbonIntensityClient(emap_key, EMAP_ZONE, logger)

        run_log_path   = log_dir / f"runs_{session_id}.jsonl"
        self.run_log   = RunLogger(run_log_path)
        logger.info(f"Run log → {run_log_path}")

        # Build reference outputs (C) for verification
        self._ref_outputs: dict[tuple[str,str], str] = {}

    # ── Pre-build all binaries ────────────────────────────────────────────────

    def build_all(self, langs: list[str], algos: list[str]) -> dict:
        """Compile everything up-front; return {(lang,algo): CompiledBinary}."""
        binaries: dict[tuple[str,str], CompiledBinary] = {}
        self.logger.info("── Build phase ──────────────────────────────────────")
        for lang in langs:
            for algo in algos:
                b = self.builder.build(lang, algo)
                binaries[(lang, algo)] = b
                status = "OK" if not b.error else "FAIL"
                self.logger.info(f"  build {lang:12s}  {algo:14s}  [{status}]")
                if b.error:
                    self.logger.warning(f"    {b.error.splitlines()[0]}")
        return binaries

    # ── Collect C reference outputs ───────────────────────────────────────────

    def collect_references(
        self,
        binaries: dict,
        algos: list[str],
        sizes: list[str],
    ):
        self.logger.info("── Reference outputs (C) ────────────────────────────")
        for algo in algos:
            b = binaries.get(("c", algo))
            if b is None or b.error:
                self.logger.warning(f"  C/{algo}: no binary — skipping reference")
                continue
            for size in sizes:
                rc, out, err, _ = self.runner.run(b, size)
                if rc == 0:
                    self._ref_outputs[(algo, size)] = normalise_output(out)
                    self.logger.debug(f"  ref C/{algo}/{size} hash={sha256_of(out)[:8]}")
                else:
                    self.logger.warning(
                        f"  C/{algo}/{size} reference run failed: {err[:80]}")

    # ── Single run with energy measurement ───────────────────────────────────

    def _timed_run(
        self,
        binary: CompiledBinary,
        size: str,
        run_index: int,
        is_warmup: bool,
    ) -> RunRecord:
        lang = binary.language
        algo = binary.algorithm

        carbon_intensity = self.carbon.get_intensity()

        # Wrap the actual subprocess call so RAPLReader can bracket it
        def _run():
            return self.runner.run(binary, size)

        start = utc_now()
        (rc, out, err, wall), pkg_j, cores_j = self.rapl.measure_run(_run)
        end = utc_now()

        norm_out = normalise_output(out)
        ref      = self._ref_outputs.get((algo, size))
        matches  = (norm_out == ref) if ref is not None and lang != "c" else None
        if lang == "c":
            matches = (rc == 0)   # C is its own reference

        energy_kwh = None
        carbon     = None
        if pkg_j is not None and carbon_intensity is not None:
            energy_kwh = pkg_j / 3_600_000.0   # J → kWh
            carbon     = energy_kwh * carbon_intensity

        rec = RunRecord(
            session_id         = self.session_id,
            run_index          = run_index,
            language           = lang,
            algorithm          = algo,
            input_size         = size,
            is_warmup          = is_warmup,
            start_utc          = start,
            end_utc            = end,
            wall_s             = round(wall, 6),
            output_matches_ref = matches,
            stdout_hash        = sha256_of(norm_out),
            rapl_package_j     = round(pkg_j,   6) if pkg_j   is not None else None,
            rapl_cores_j       = round(cores_j, 6) if cores_j is not None else None,
            carbon_intensity_gco2_kwh = carbon_intensity,
            energy_kwh         = round(energy_kwh, 12) if energy_kwh else None,
            carbon_gco2e       = round(carbon,    10) if carbon      else None,
            returncode         = rc,
            stderr_snippet     = err[:200],
            error              = "" if rc == 0 else f"rc={rc}",
        )
        return rec

    # ── Main loop ─────────────────────────────────────────────────────────────

    def run_all(
        self,
        langs: list[str],
        algos: list[str],
        sizes: list[str],
    ) -> list[RunRecord]:
        binaries = self.build_all(langs, algos)

        if self.dry_run:
            self.logger.info("Dry run — skipping timed runs.")
            return []

        self.collect_references(binaries, algos, sizes)

        all_records: list[RunRecord] = []
        total_combos = len(langs) * len(algos) * len(sizes)
        done = 0

        self.logger.info("── Benchmark runs ───────────────────────────────────")

        for lang in langs:
            for algo in algos:
                binary = binaries.get((lang, algo))
                if binary is None or binary.error:
                    self.logger.warning(
                        f"  Skipping {lang}/{algo}: binary unavailable")
                    done += len(sizes)
                    continue

                for size in sizes:
                    done += 1
                    self.logger.info(
                        f"  [{done}/{total_combos}]  "
                        f"{lang:12s}  {algo:14s}  {size:6s}  "
                        f"(warmup×{self.n_warmup} + runs×{self.n_runs})"
                    )

                    # ── Warm-up phase ──────────────────────────────────────
                    run_warmup(binary, size, self.n_warmup,
                               self.runner, self.logger)

                    # Also log warm-up records (marked is_warmup=True)
                    # so the full history is preserved in JSONL even though
                    # they are excluded from analysis
                    for wi in range(self.n_warmup):
                        rec = self._timed_run(binary, size,
                                              run_index=wi + 1,
                                              is_warmup=True)
                        self.run_log.write(rec)

                    # ── Timed runs ─────────────────────────────────────────
                    combo_records = []
                    for ri in range(1, self.n_runs + 1):
                        rec = self._timed_run(binary, size,
                                              run_index=ri,
                                              is_warmup=False)
                        self.run_log.write(rec)
                        combo_records.append(rec)
                        all_records.append(rec)

                        status = "✓" if rec.output_matches_ref != False else "✗"
                        energy_str = (
                            f"  {rec.rapl_package_j:.3f}J"
                            if rec.rapl_package_j is not None else "  --J"
                        )
                        carbon_str = (
                            f"  {rec.carbon_gco2e*1e6:.2f}µgCO2e"
                            if rec.carbon_gco2e is not None else ""
                        )
                        self.logger.debug(
                            f"    run {ri:2d}/{self.n_runs}  "
                            f"{status}  wall={rec.wall_s:.4f}s"
                            f"{energy_str}{carbon_str}"
                        )

                    # Per-combo mini-summary
                    walls = [r.wall_s for r in combo_records]
                    fails = [r for r in combo_records
                             if r.output_matches_ref is False]
                    self.logger.info(
                        f"    → wall: min={min(walls):.4f}s  "
                        f"mean={sum(walls)/len(walls):.4f}s  "
                        f"max={max(walls):.4f}s  "
                        f"output_errors={len(fails)}"
                    )

        self.run_log.close()
        return all_records

    def cleanup(self):
        shutil.rmtree(self._tmp, ignore_errors=True)

# ─────────────────────────────────────────────────────────────────────────────
# Post-run reports
# ─────────────────────────────────────────────────────────────────────────────

def write_csv_summary(records: list[RunRecord], path: Path):
    """Write one row per timed run to CSV — ready for R/pandas analysis."""
    if not records:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(asdict(records[0]).keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in records:
            w.writerow(asdict(r))


def write_json_report(records: list[RunRecord],
                      session_id: str, path: Path):
    """Write aggregated per-combo statistics to JSON."""
    from collections import defaultdict
    import statistics as stats

    groups: dict[tuple, list[RunRecord]] = defaultdict(list)
    for r in records:
        if not r.is_warmup:
            groups[(r.language, r.algorithm, r.input_size)].append(r)

    report = {"session_id": session_id, "combos": []}
    for (lang, algo, size), recs in sorted(groups.items()):
        walls   = [r.wall_s for r in recs]
        pkg_js  = [r.rapl_package_j for r in recs if r.rapl_package_j is not None]
        carbons = [r.carbon_gco2e   for r in recs if r.carbon_gco2e   is not None]
        fails   = sum(1 for r in recs if r.output_matches_ref is False)

        def agg(vals):
            if not vals:
                return None
            return {
                "n":      len(vals),
                "mean":   round(stats.mean(vals), 8),
                "median": round(stats.median(vals), 8),
                "stdev":  round(stats.stdev(vals), 8) if len(vals) > 1 else 0,
                "min":    round(min(vals), 8),
                "max":    round(max(vals), 8),
            }

        report["combos"].append({
            "language":    lang,
            "algorithm":   algo,
            "input_size":  size,
            "n_runs":      len(recs),
            "output_errors": fails,
            "wall_s":      agg(walls),
            "rapl_package_j": agg(pkg_js) if pkg_js else None,
            "carbon_gco2e":   agg(carbons) if carbons else None,
        })

    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)


def print_final_table(records: list[RunRecord], logger: logging.Logger):
    """Print a quick wall-time summary table to the console."""
    from collections import defaultdict
    import statistics as stats

    groups: dict[tuple, list[float]] = defaultdict(list)
    for r in records:
        if not r.is_warmup:
            groups[(r.language, r.algorithm, r.input_size)].append(r.wall_s)

    logger.info("\n" + "═" * 70)
    logger.info(f"{'LANG':12s}  {'ALGORITHM':14s}  {'SIZE':6s}  "
                f"{'MEAN(s)':>9}  {'STDEV':>8}  {'N':>4}")
    logger.info("═" * 70)
    for (lang, algo, size) in sorted(groups):
        ws = groups[(lang, algo, size)]
        mean  = stats.mean(ws)
        stdev = stats.stdev(ws) if len(ws) > 1 else 0
        logger.info(f"{lang:12s}  {algo:14s}  {size:6s}  "
                    f"{mean:9.4f}  {stdev:8.4f}  {len(ws):4d}")
    logger.info("═" * 70)

# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def parse_args():
    here = Path(__file__).parent
    p = argparse.ArgumentParser(
        description="Carbon footprint benchmark harness — orchestrates runs, "
                    "warm-ups, RAPL energy logging, and carbon conversion."
    )
    p.add_argument("--impl-dir",  default=str(here / "implementations"),
                   help="Root of per-language implementation folders")
    p.add_argument("--log-dir",   default=str(here / "logs"),
                   help="Directory for run logs and reports")
    p.add_argument("--runs",      type=int, default=30,
                   help="Timed runs per (lang, algo, size) combination (default 30)")
    p.add_argument("--warmup",    type=int, default=5,
                   help="Warm-up runs to discard before timing (default 5)")
    p.add_argument("--lhm-url",   default=os.environ.get("LHM_URL", "http://localhost:8085"),
                   help="LibreHardwareMonitor HTTP API base URL")
    p.add_argument("--emap-key",  default=os.environ.get("EMAP_API_KEY", ""),
                   help="Electricity Maps API key")
    p.add_argument("--algo",   choices=ALGORITHMS, default=None)
    p.add_argument("--lang",   choices=LANGUAGES,  default=None)
    p.add_argument("--size",   choices=INPUT_SIZES, default=None)
    p.add_argument("--dry-run",   action="store_true",
                   help="Build only — no timed runs (smoke test)")
    p.add_argument("--verbose",  "-v", action="store_true")
    return p.parse_args()


def make_session_id() -> str:
    return datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%S")


def main():
    args       = parse_args()
    session_id = make_session_id()

    log_dir  = Path(args.log_dir)
    impl_dir = Path(args.impl_dir)

    logger = setup_logging(log_dir, args.verbose, session_id)
    logger.info(f"Session ID      : {session_id}")
    logger.info(f"Implementation  : {impl_dir.resolve()}")
    logger.info(f"Log directory   : {log_dir.resolve()}")
    logger.info(f"Runs / combo    : {args.runs}")
    logger.info(f"Warm-up / combo : {args.warmup}")
    logger.info(f"LHM URL         : {args.lhm_url}")
    logger.info(f"Electricity Maps: {'key set' if args.emap_key else 'NO KEY — carbon will be null'}")
    logger.info(f"Platform        : {platform.platform()}")

    if not impl_dir.exists():
        logger.error(f"--impl-dir '{impl_dir}' does not exist.")
        sys.exit(1)

    langs = [args.lang]   if args.lang else LANGUAGES
    algos = [args.algo]   if args.algo else ALGORITHMS
    sizes = [args.size]   if args.size else INPUT_SIZES

    harness = Harness(
        impl_dir   = impl_dir,
        log_dir    = log_dir,
        n_runs     = args.runs,
        n_warmup   = args.warmup,
        lhm_url    = args.lhm_url,
        emap_key   = args.emap_key,
        session_id = session_id,
        logger     = logger,
        dry_run    = args.dry_run,
    )

    try:
        records = harness.run_all(langs, algos, sizes)
    finally:
        harness.cleanup()

    if not args.dry_run and records:
        csv_path  = log_dir / f"results_{session_id}.csv"
        json_path = log_dir / f"report_{session_id}.json"
        write_csv_summary(records, csv_path)
        write_json_report(records, session_id, json_path)
        logger.info(f"CSV  → {csv_path}")
        logger.info(f"JSON → {json_path}")
        print_final_table(records, logger)

    fails = [r for r in records if r.output_matches_ref is False]
    if fails:
        logger.warning(f"{len(fails)} run(s) produced output that did NOT match "
                       "the C reference. Review before using energy data.")
        sys.exit(2)

    logger.info("All done.")
    sys.exit(0)


if __name__ == "__main__":
    main()