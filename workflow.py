"""
LHM web server connect
Electricity Map API
j -> kWh -> gCO2e

"""

import os
import requests
import sys
import time
import json
import argparse
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
import ssl


LHM_URL = "http://172.22.1.29:8085/data.json"
EM_ZONE = "US-NY-NYIS"
EMAP_API_KEY = "zyjqZja8pJXqecWbs6d2"
EM_URL = f"https://api.electricitymaps.com/v3/carbon-intensity/latest?zone={EM_ZONE}"
SAMPLE_SECS   = 5      # how long to sample LHM wattage
SAMPLE_HZ     = 4      # polls per second


# response = requests.get(
#     # "https://api.electricitymaps.com/v3/carbon-intensity/latest",
#     EM_URL,
#     headers={
#         "auth-token": EMAP_API_KEY
#     }
# )
# print(response.json())

def bold(s):  return f"\033[1m{s}\033[0m"
def green(s): return f"\033[92m{s}\033[0m"
def red(s):   return f"\033[91m{s}\033[0m"
def yellow(s):return f"\033[93m{s}\033[0m"
 
def fetch_json(url, headers=None, timeout=8):
    try:
        r = requests.get(url, headers=headers or {}, timeout=timeout, verify=False)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.HTTPError as e:
        raise OSError(f"HTTP {e.response.status_code} {e.response.reason}: {e.response.text[:200]}") from e
    except Exception as e:
        raise OSError(f"Failed to fetch {url}: {e}") from e


def find_cpu_power(node, results=None):
    """Recursively search LHM JSON tree for CPU Package power sensor."""
    if results is None:
        results = []
    text = node.get("Text", "")
    sensor_type = node.get("Type", "")
    
    if "Power" in sensor_type or "power" in text.lower():
        value = node.get("Value", "")
        min_v = node.get("Min", "")
        max_v = node.get("Max", "")
        results.append({
            "name": text,
            "value": value,
            "min": min_v,
            "max": max_v,
            "id": node.get("id", "")
        })
    for child in node.get("Children", []):
        find_cpu_power(child, results)
    return results
 
def parse_watts(value_str):
    """Parse '45.2 W' -> 45.2, returns None on failure."""
    try:
        return float(value_str.replace("W", "").replace(",", ".").strip())
    except (ValueError, AttributeError):
        return None
 
# ─── Test 1: LHM connectivity ─────────────────────────────────────────────────
def test_lhm_connect():
    print(bold("\n[1/3] LHM Connect"))
    try:
        data = fetch_json(LHM_URL)
        print(green(f"✓ Connected to {LHM_URL}"))
        return data
    except OSError as e:
        print(red(f"✗ Could not connect to {LHM_URL}"))
        print(yellow(f"  Ensure LibreHardwareMonitor is running with Web Server enabled"))
        print(yellow(f"  Error: {str(e)}"))
        return None
 
# LMH power reading
def test_lhm_power(data):
    print(bold("\n[2/3] LHM — CPU power readings"))
    if data is None:
        print(yellow(" no connectionS"))
        return None
 
    sensors = find_cpu_power(data)
    if not sensors:
        print(red(" No power sensors found in LHM data"))
        return None
 
    print(f"  Found {len(sensors)} power sensor(s):")
    for s in sensors:
        print(f"    • {s['name']:<35} {s['value']:>10}   (min {s['min']}, max {s['max']})")
 
    # Pick best candidate: prefer "CPU Package"
    pkg = next((s for s in sensors if "Package" in s["name"]), sensors[0])
    watts = parse_watts(pkg["value"])
    if watts is None:
        print(red(f"  ✗ Could not parse wattage from '{pkg['value']}'"))
        return None
 
    print(green(f"\n  ✓ Using sensor: '{pkg['name']}' → {watts:.2f} W"))
 
    # Sample for SAMPLE_SECS seconds
    print(f"\n  Sampling for {SAMPLE_SECS}s at {SAMPLE_HZ} Hz ...")
    readings = []
    interval = 1.0 / SAMPLE_HZ
    for i in range(SAMPLE_SECS * SAMPLE_HZ):
        try:
            d = fetch_json(LHM_URL)
            s_list = find_cpu_power(d)
            p = next((s for s in s_list if "Package" in s["name"]), s_list[0] if s_list else None)
            if p:
                w = parse_watts(p["value"])
                if w is not None:
                    readings.append(w)
                    print(f"    [{i+1:02d}] {w:.2f} W", end="\r")
        except Exception:
            pass
        time.sleep(interval)
 
    if not readings:
        print(red(" No readings collected during sampling"))
        return None
 
    avg_w  = sum(readings) / len(readings)
    energy_j   = avg_w * SAMPLE_SECS          # joules = watts × seconds
    energy_kwh = energy_j / 3_600_000         # 1 kWh = 3,600,000 J
 
    print(f"\n  Samples   : {len(readings)}")
    print(f"  Avg power : {avg_w:.3f} W")
    print(f"  Energy    : {energy_j:.4f} J  ({energy_kwh:.8f} kWh) over {SAMPLE_SECS}s")
    print(green("  ✓ LHM power sampling validated"))
    return {"avg_watts": avg_w, "energy_j": energy_j, "energy_kwh": energy_kwh}
 
# ─── Test 3: Electricity Maps API ─────────────────────────────────────────────
def test_electricity_maps(token, lhm_result):
    print(bold("\n[3/3] Electricity Maps API — carbon intensity"))
 
    if not token:
        print(yellow("  ⚠ No token provided. Skipping live API call.\n\n  → Run with: python workflow.py --em-token YOUR_TOKEN \n\n"))
        return
 
    headers = {"auth-token": token}
    try:
        data = fetch_json(EM_URL, headers=headers)
    except OSError as e:
        print(red(f"  ✗ Connection error: {str(e)}"))
        return
 
    ci = data.get("carbonIntensity")
    zone = data.get("zone", "unknown")
    dt = data.get("datetime", "unknown")
 
    if ci is None:
        print(red(f"  ✗ Unexpected response: {data}"))
        return
 
    print(green(f"  ✓ Zone         : {zone}"))
    print(green(f"  ✓ Timestamp    : {dt}"))
    print(green(f"  ✓ Carbon intens: {ci} gCO2/kWh"))
 
    # Full pipeline calculation
    if lhm_result:
        kwh = lhm_result["energy_kwh"]
        gco2e = kwh * ci
        print(bold(f"\n  ── Pipeline smoke test ({SAMPLE_SECS}s window) ──"))
        print(f"  Energy      : {kwh:.8f} kWh")
        print(f"  Carbon intns: {ci} gCO2/kWh")
        print(f"  gCO2e       : {gco2e:.8f} gCO2e")
        print(green("  ✓ Full pipeline (LHM → kWh → gCO2e) validated"))
 

def main():
    parser = argparse.ArgumentParser(description="Validate measurement tools for carbon footprint research")
    parser.add_argument("--em-token", default="", help="Electricity Maps API token")
    args = parser.parse_args()
 
    print(bold("=" * 55))
    print(bold("  Tool Validation — Carbon Footprint Research"))
    print(bold("=" * 55))
 
    lhm_data   = test_lhm_connect()
    lhm_result = test_lhm_power(lhm_data)
    test_electricity_maps(args.em_token, lhm_result)
 
    print(bold("\n" + "=" * 55))
    print("Done. Fix any ✗ items before proceeding to Phase 2.\n")
 
if __name__ == "__main__":
    main()