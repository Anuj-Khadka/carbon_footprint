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
MAIN_RUNS     = 115
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