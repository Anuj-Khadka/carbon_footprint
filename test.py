"""
pilot_study.py  –  Carbon Footprint Benchmark  (build-up version)
Step 1: LHM sensor reading
"""

import requests


LHM_URL = "http://172.22.1.29:8085/data.json"


def get_rapl_energy_joules() -> float:
    """
    Query LibreHardwareMonitor's REST API and return the current
    CPU Package RAPL energy counter in Joules.

    LHM exposes a tree of sensor nodes at /data.json.
    We walk the tree looking for a sensor whose name contains
    'CPU Package' and whose SensorType is 'Energy' (unit: J).

    Returns the float value, or raises RuntimeError if not found.
    """
    response = requests.get(LHM_URL)

    data = response.json() 
    # return data

    def search(node: dict) -> float | None:
        # Check if this node is the RAPL energy sensor we want
        name = node.get("Text", "")
        sensor_type = node.get("SensorType", "")
        value_str = node.get("Value", "")

        if "CPU Package" in name and sensor_type == "Energy":
            # Value comes back as e.g. "12.34 J" – strip the unit
            try:
                return float(value_str.split()[0])
            except (ValueError, IndexError):
                pass

        # Recurse into children
        for child in node.get("Children", []):
            result = search(child)
            if result is not None:
                return result

        return None

    joules = search(data)
    if joules is None:
        raise RuntimeError(
            "RAPL 'CPU Package' energy sensor not found in LHM response. "
            "Make sure LibreHardwareMonitor is running and the sensor is enabled."
        )
    return joules


# ── quick smoke-test ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Testing LHM sensor reading...")
    try:
        j = get_rapl_energy_joules()
        print(f"  CPU Package RAPL energy: {j} J  ✓")
    except Exception as e:
        print(f"  ERROR: {e}")