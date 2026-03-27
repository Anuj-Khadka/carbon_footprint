import requests
import json

r = requests.get('http://localhost:8085/data.json')
data = r.json()
print('LibreHardwareMonitor OK')

def find_power(node):
    if isinstance(node, dict):
        text = node.get('Text', '')
        value = node.get('Value', '')
        if 'Power' in text and value and value != '0.0 W':
            print(f'  {text}: {value}')
        for child in node.get('Children', []):
            find_power(child)

find_power(data)