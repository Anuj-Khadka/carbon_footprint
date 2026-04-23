# connect to the 172 url.


import requests


response = requests.get("http://172.22.1.29:8085/data.json")
print(response.status_code)
print(response.text)