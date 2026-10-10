"""
List fleets and query a whole fleet using httpx

A fleet is a named group of sites. Any time-series query accepts
`fleet=<id>` in place of `sites=site1,site2,...`.
"""

import json
import os
import sys
from datetime import datetime, timedelta

import httpx

# Configuration
base_url = os.getenv("PS_API_URL", "https://app.phisaver.com").rstrip("/")
username = os.getenv("PS_API_USERNAME")
password = os.getenv("PS_API_PASSWORD")

if not username or not password:
    print("Error: Set PS_API_USERNAME and PS_API_PASSWORD environment variables")
    sys.exit(1)

# Authenticate
auth_response = httpx.post(f"{base_url}/api/v2/token/", data={"username": username, "password": password})
if auth_response.status_code != httpx.codes.OK:
    print(f"Authentication failed: {auth_response.status_code}")
    sys.exit(1)

client = httpx.Client(
    base_url=base_url,
    headers={"Authorization": f"Token {auth_response.json()['token']}"},
    timeout=60,
)

# List fleets
fleets = client.get("/api/v2/fleets/").json()
print(f"Found {len(fleets)} fleet(s)")
for fleet in fleets:
    print(f"  {fleet['name']} ({fleet['id']}): {fleet['site_count']} site(s), timezone {fleet['timezone']}")

if not fleets:
    print("This account has no fleets.")
    sys.exit(0)

# Fleet details include its sites
fleet_id = fleets[0]["id"]
detail = client.get(f"/api/v2/fleets/{fleet_id}/").json()
print(f"\nFleet '{fleet_id}' details:")
print(json.dumps(detail, indent=2)[:1500])

# Daily energy for every site in the fleet, last 30 days
end_date = datetime.now().astimezone()
start_date = end_date - timedelta(days=30)
table = client.get(
    "/api/v2/ts/table/",
    params={
        "fleet": fleet_id,  # Equivalent to sites=<every site in the fleet>
        "start": start_date.isoformat(),
        "stop": end_date.isoformat(),
        "mets": "Production,Consumption",
        "units": "kWh/day",
    },
)
print(f"\nFleet table ({table.status_code}):")
print(json.dumps(table.json(), indent=2))
