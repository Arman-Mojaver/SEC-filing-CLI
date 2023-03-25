import requests
import json


url = f'https://data.sec.gov/submissions/CIK0000320193.json'

response = requests.get(url, headers={"User-Agent": "arman@mojaver.com"})
data = json.loads(s=response.content.decode())

print(data)


