import requests

# A Census API URL always has this shape:
# https://api.census.gov/data/{year}/{dataset}?get={variables}&for={geography}

YEAR = 2020
DATASET = "dec/pl"
URL = f"https://api.census.gov/data/{YEAR}/{DATASET}"
API_KEY = "6b4c0edff74623751b8b067569e3f6cc6c6663ce"

params = {
    "get": "NAME,P1_001N",
    "for": "state:*",
    "key": API_KEY,
}

response = requests.get(URL, params=params)

if response.status_code != 200:
    print(f"Request failed ({response.status_code})")
    print(response.text)
    raise SystemExit(1)

response.raise_for_status()
data = response.json()

# The API returns a list of lists. The first row is the column headers

print(f"Got {len(data) - 1} rows back.")

for i in data:
    print(i)
