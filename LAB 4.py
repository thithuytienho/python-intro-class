############################################
# Census API CLI APP LAB.4, 2026 (C)       #
# Thi Thuy Tien Ho # thithuytienho@usf.edu #
#------------------------------------------#

import requests

# A Census API URL always has this shape:
# https://api.census.gov/data/{year}/{dataset}?get={variables}&for={geography}

YEAR = 2020
DATASET = "dec/pl"
URL = f"https://api.census.gov/data/{YEAR}/{DATASET}"
API_KEY = "6b4c0edff74623751b8b067569e3f6cc6c6663ce"

# Ask the user for the State FIPS code
state_fips = input("Enter the State FIPS code that you would like data for").strip()

# Ask the user for the variable names
variables = input("Enter the variable names that you would like data for").strip()

params = {
    "get": f"NAME,{variables}",
    "for": f"state:{state_fips}",
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