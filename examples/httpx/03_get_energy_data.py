"""
Retrieve time-series energy data using httpx

This example shows how to:
- Get time-series data for specific metrics (e.g., Production, Consumption)
- Specify time ranges and binning intervals
- Access data in both series and table formats
- Query metrics by category
- Handle error responses
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

# Step 1: Authenticate
auth_response = httpx.post(f"{base_url}/api/v2/token/", json={"email": username, "password": password})
if auth_response.status_code != httpx.codes.OK:
    print(f"Authentication failed: {auth_response.status_code}")
    sys.exit(1)

client = httpx.Client(
    base_url=base_url,
    headers={"Authorization": f"Bearer {auth_response.json()['access']}"},
    timeout=60,
)
print("Authenticated\n")

# Step 2: Pick sites to query. Prefer a site with configured metrics
# (needed for metcat queries), plus a second site for the multi-site table.
sites = client.get("/api/v2/sites/").json()
if not sites:
    print("No sites available for this account")
    sys.exit(1)
site = next(
    (s for s in sites if client.get(f"/api/v2/sites/{s['id']}/metrics/").json()),
    sites[0],
)
site_id = site["id"]
site_ids = [site_id, *[s["id"] for s in sites if s["id"] != site_id][:1]]

# Step 3: Choose a time range: the 30 days before the site's latest data
# (falls back to the last 30 days if the site has never reported).
last_data_at = site["last_data_at"]
end_date = datetime.fromisoformat(last_data_at) if last_data_at else datetime.now().astimezone()
start_date = end_date - timedelta(days=30)
print(f"Querying {site_ids} from {start_date.isoformat()} to {end_date.isoformat()}")

# Example 1: Time series data for two metrics.
# Lists such as sites and mets are passed as ONE comma-separated string.
print("=" * 60)
print("Fetching time series data...")
series_response = client.get(
    "/api/v2/ts/series/",
    params={
        "sites": site_id,
        "start": start_date.isoformat(),
        "stop": end_date.isoformat(),
        "bin": "1d",  # Daily bins: 1d, 1h, 15min, etc.
        "mets": "Consumption,Production",  # Metrics: Production, Consumption, Net, etc.
        "units": "W",  # Units: W, kW, kWh/day, $/day
    },
)

if series_response.status_code == httpx.codes.OK:
    print("\nSeries data retrieved:")
    print(json.dumps(series_response.json(), indent=4))
else:
    print(f"Failed: {series_response.status_code}")
    print(series_response.text)

# Example 2: Table format (one value per metric, no timestamps) for multiple sites
print("\n" + "=" * 60)
print("Fetching multiple sites with data in table format...")
table_response = client.get(
    "/api/v2/ts/table/",
    params={
        "sites": ",".join(site_ids),  # Multiple sites
        "start": start_date.isoformat(),
        "stop": end_date.isoformat(),
        "units": "kWh/day",
    },
)

if table_response.status_code == httpx.codes.OK:
    print("\nTable data retrieved:")
    for site, metrics in table_response.json().items():
        print(f"  Site: {site}")
        print(json.dumps(metrics, indent=4))
else:
    print(f"Failed: {table_response.status_code}")
    print(table_response.text)

# Example 3: All metrics in a category
print("\n" + "=" * 60)
print("Fetching metrics by category (load)...")
multi_response = client.get(
    "/api/v2/ts/series/",
    params={
        "sites": site_id,
        "start": start_date.isoformat(),
        "stop": end_date.isoformat(),
        "bin": "1d",
        "metcat": "load",  # Category: load, production, battery, net, calc, other, all
        "units": "kWh/day",
    },
)

if multi_response.status_code == httpx.codes.OK:
    print("\nMetrics by category retrieved:")
    print(json.dumps(multi_response.json(), indent=4))
else:
    print(f"Failed: {multi_response.status_code}")
    print(multi_response.text)

# Example 4: View the error response
print("\n" + "=" * 60)
print("Attempting to fetch data with invalid parameters...")
invalid_response = client.get(
    "/api/v2/ts/series/",
    params={
        "sites": site_id,
        "start": start_date.isoformat(),
        "stop": end_date.isoformat(),
        "bin": "1h",
        "metcat": "InvalidMetric",  # Invalid metric category
        "units": "W",
    },
)

if invalid_response.status_code == httpx.codes.OK:
    print("Data retrieved (unexpected!)")
else:
    print("OK: the expected error occurred.")
    print(f"Status: {invalid_response.status_code}")
    print(invalid_response.text)
