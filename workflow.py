"""
LHM web server connect
Electricity Map API
j -> kWh -> gCO2e

"""

import sys
import time
import json



# LHM_URL = "https://localhost:8080/data.json"
# EM_ZONE = "x"
# EM_URL = 

import requests

response = requests.get(
    "https://api.electricitymaps.com/v3/carbon-intensity/latest",
    headers={
        "auth-token": f"zyjqZja8pJXqecWbs6d2"
    }
)
print(response.json())