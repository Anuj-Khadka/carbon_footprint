"""
pilot_study.py  –  Carbon Footprint Benchmark  (build-up version)
Step 1: LHM sensor reading
"""


import requests
import time 
import subprocess
import sys
import os


LHM_URL = "http://172.22.1.29:8085/data.json"


def get_cpu_package_watts() -> float:
    """
    Query LibreHardwareMonitor's REST API and return the current
    CPU Package power draw in watts.
    """
    response = requests.get(LHM_URL)

    data = response.json() 
    print(data)

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




if __name__ == "__main__":
    exe = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "implementations",
        "c",
        "summation",
        "summation_small.exe",
    )

    print(f"Launching: {exe}")

    proc = subprocess.Popen(
        exe,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    ready = proc.stdout.readline().strip()
    if ready != "ready":
        print("Algorithm did not signal READY. Exiting.")
        proc.terminate()
        sys.exit(1)

    print(f"process ready.")

    for i in range(5):
        joules, checksum = run_once(proc)
        print(f"Run {i+1}: Energy = {joules:.2f} J, Checksum = {checksum}")
        
    proc.stdin.close()
    proc.wait()
    print("All runs completed. Process terminated.")
