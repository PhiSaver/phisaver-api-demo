"""
Retrieve heatmap data using httpx

The heatmap endpoint returns [day_of_year, hour, value] points for one site, convenient for plotting
time-of-day vs day patterns (e.g. when a site imports from the grid).
Heatmap values are always in Watts.
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
auth_response = httpx.post(f"{base_url}/api/v2/token/", json={"email": username, "password": password})
if auth_response.status_code != httpx.codes.OK:
    print(f"Authentication failed: {auth_response.status_code}")
    sys.exit(1)

client = httpx.Client(
    base_url=base_url,
    headers={"Authorization": f"Bearer {auth_response.json()['access']}"},
    timeout=60,
)

# Pick the first site and the 7 days before its latest data
sites = client.get("/api/v2/sites/").json()
if not sites:
    print("No sites available for this account")
    sys.exit(1)
site = sites[0]
end_date = datetime.fromisoformat(site["last_data_at"]) if site["last_data_at"] else datetime.now().astimezone()
start_date = end_date - timedelta(days=7)

print(f"Fetching heatmap for '{site['id']}'...")
response = client.get(
    "/api/v2/ts/heatmap/",
    params={
        "sites": site["id"],
        "start": start_date.isoformat(),
        "stop": end_date.isoformat(),
        "mets": "Net",  # One or more comma-separated metrics
    },
)

if response.status_code != httpx.codes.OK:
    print(f"Failed: {response.status_code}")
    print(response.text)
    sys.exit(1)

# Response shape: {site: {metric: [[day_of_year (1-365), hour (0-23), watts], ...]}}
for site_id, metrics in response.json().items():
    for metric, points in metrics.items():
        print(f"{site_id} / {metric}: {len(points)} points")
        print(json.dumps(points[:5], indent=2))
