"""
pilot_study.py  –  Carbon Footprint Benchmark  (build-up version)
Step 1: LHM sensor reading
"""

import requests


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
        sensor_id = node.get("SensorId", "")
        value_str = node.get("Value", "")
 
        if sensor_id == "/intelcpu/0/power/0":
            try:
                return float(value_str.split()[0])  # strip " W"
            except (ValueError, IndexError):
                pass
 
        for child in node.get("Children", []):
            result = search(child)
            if result is not None:
                return result
 
        return None
 
    watts = search(data)
    if watts is None:
        raise RuntimeError(
            "CPU Package power sensor not found in LHM response. "
            "Make sure LibreHardwareMonitor is running."
        )
    return watts


# ── quick smoke-test ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Testing LHM sensor reading...")
    try:
        w = get_cpu_package_watts()
        print(f"  CPU Package power: {w} W  ✓")
    except Exception as e:
        print(f"  ERROR: {e}")