"""
pilot_study.py  –  Carbon Footprint Benchmark  (build-up version)
Step 1: LHM sensor reading
"""


import requests
import time 
import subprocess


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


if __name__ == "__main__":
    print("Testing LHM sensor reading...")
    try:
        w = get_cpu_package_watts()
        print(f"  CPU Package power: {w} W  ✓")
    except Exception as e:
        print(f"  ERROR: {e}")