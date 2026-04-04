import csv
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPETITIONS = 5
OUTPUT_CSV = "benchmark_results.csv"
BASE_DIR = Path(__file__).resolve().parent
EXE_EXT = ".exe" if sys.platform.startswith("win") else ""

# Edit this section for your actual programs
BENCHMARKS = [
    {
        "algorithm": "merge_sort",
        "sizes": [10000, 50000, 100000, 500000],
        "programs": [
            {
                "language": "c",
                "command": [str(BASE_DIR / "c" / "bin" / f"merge_sort{EXE_EXT}")],
            },
            {
                "language": "python",
                "command": [sys.executable, str(BASE_DIR / "python" / "merge_sort.py")],
            },
            {
                "language": "java",
                "command": ["java", "-cp", str(BASE_DIR / "java"), "MergeSort"],
            },
            {
                "language": "javascript",
                "command": ["node", str(BASE_DIR / "javascript" / "merge_sort.js")],
            },
            {
                "language": "rust",
                "command": [
                    str(BASE_DIR / "rust" / "merge_sort" / "target" / "release" / f"merge_sort{EXE_EXT}")
                ],
            },
        ],
    },
    {
        "algorithm": "matrix_multiply",
        "sizes": [100, 200, 300, 400],
        "programs": [
            {
                "language": "c",
                "command": [str(BASE_DIR / "c" / "bin" / f"matrix_multiplication{EXE_EXT}")],
            },
            {
                "language": "python",
                "command": [sys.executable, str(BASE_DIR / "python" / "matrix_multiplication.py")],
            },
            {
                "language": "java",
                "command": ["java", "-cp", str(BASE_DIR / "java"), "MatrixMultiplication"],
            },
            {
                "language": "javascript",
                "command": ["node", str(BASE_DIR / "javascript" / "matrix_multiplication.js")],
            },
            {
                "language": "rust",
                "command": [
                    str(
                        BASE_DIR
                        / "rust"
                        / "matrix_multiplication"
                        / "target"
                        / "release"
                        / f"matrix_multiplication{EXE_EXT}"
                    )
                ],
            },
        ],
    },
]


def run_command(command: list[str], timeout: int = 300) -> tuple[float, str, str, int]:
    """
    Run a command and measure wall-clock runtime.
    Returns:
        runtime_seconds, stdout, stderr, return_code
    """
    start = time.perf_counter()
    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=timeout
    )
    end = time.perf_counter()

    runtime = end - start
    return runtime, completed.stdout.strip(), completed.stderr.strip(), completed.returncode


def ensure_program_exists(command: list[str]) -> bool:
    """
    Basic check: for local executables/scripts, verify the file exists when relevant.
    """
    first = Path(command[0])

    def try_build_missing_c_executable(exe_path: Path) -> bool:
        """
        If a C executable is missing, attempt to build it from a matching .c file.
        """
        gcc_path = shutil.which("gcc")
        if not gcc_path:
            return False

        source_candidates = [
            exe_path.with_suffix(".c"),
            exe_path.parent.parent / f"{exe_path.stem}.c",
            BASE_DIR / "c" / f"{exe_path.stem}.c",
        ]

        source_path = next((p for p in source_candidates if p.exists()), None)
        if not source_path:
            return False

        exe_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            subprocess.run(
                [gcc_path, str(source_path), "-O2", "-o", str(exe_path)],
                capture_output=True,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError:
            return False

        return exe_path.exists()

    # First token can be an absolute/relative executable path.
    if first.is_absolute() or any(sep in command[0] for sep in ("/", "\\")):
        if not first.exists():
            if first.suffix in (".exe", "") and "c" in first.parts:
                if try_build_missing_c_executable(first):
                    return True
            return False

    # Script-based command where second token is a local script path.
    if len(command) > 1 and command[1].endswith((".py", ".js")):
        if not Path(command[1]).exists():
            return False

    return True


def main() -> None:
    rows = []

    for benchmark in BENCHMARKS:
        algorithm = benchmark["algorithm"]
        sizes = benchmark["sizes"]

        for size in sizes:
            for program in benchmark["programs"]:
                language = program["language"]
                base_command = program["command"]

                if not ensure_program_exists(base_command):
                    print(f"[SKIP] Missing program for {algorithm} / {language}: {base_command}")
                    continue

                for rep in range(1, REPETITIONS + 1):
                    command = base_command + [str(size)]

                    print(f"Running: algorithm={algorithm}, language={language}, size={size}, rep={rep}")

                    try:
                        runtime, stdout, stderr, return_code = run_command(command)
                    except subprocess.TimeoutExpired:
                        rows.append({
                            "algorithm": algorithm,
                            "language": language,
                            "input_size": size,
                            "rep": rep,
                            "runtime_seconds": "",
                            "return_code": "TIMEOUT",
                            "stdout": "",
                            "stderr": "Process timed out"
                        })
                        print("  -> TIMEOUT")
                        continue
                    except Exception as exc:
                        rows.append({
                            "algorithm": algorithm,
                            "language": language,
                            "input_size": size,
                            "rep": rep,
                            "runtime_seconds": "",
                            "return_code": "ERROR",
                            "stdout": "",
                            "stderr": str(exc)
                        })
                        print(f"  -> ERROR: {exc}")
                        continue

                    rows.append({
                        "algorithm": algorithm,
                        "language": language,
                        "input_size": size,
                        "rep": rep,
                        "runtime_seconds": f"{runtime:.6f}",
                        "return_code": return_code,
                        "stdout": stdout,
                        "stderr": stderr
                    })

                    print(f"  -> done in {runtime:.6f}s")

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "algorithm",
                "language",
                "input_size",
                "rep",
                "runtime_seconds",
                "return_code",
                "stdout",
                "stderr",
            ]
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nSaved results to: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()