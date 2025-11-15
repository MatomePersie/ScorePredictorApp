import requests

API_KEY = "206b7f91de16477f840fafd142941d92"
BASE_URL = "https://api.football-data.org/v4/"
HEADERS = {"X-Auth-Token": API_KEY}

url = BASE_URL + "matches"
r = requests.get(url, headers=HEADERS)
data = r.json()

print(data.keys())
print(len(data.get("matches", [])))
print(data.get("matches", [])[0] if len(data.get("matches", [])) > 0 else "No matches found")
