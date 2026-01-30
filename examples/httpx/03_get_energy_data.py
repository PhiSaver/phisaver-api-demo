"""
Retrieve time-series energy data using httpx

This example shows how to:
- Get time-series data for specific metrics (e.g., Production, Consumption)
- Specify time ranges and binning intervals
- Access data in both series and table formats
- Handle multiple metrics and error responses
"""

import os
import httpx
import json
from datetime import datetime
from zoneinfo import ZoneInfo

# Configuration
base_url = os.getenv("PHISAVER_URL", "https://app.phisaver.com")
username = os.getenv("PHISAVER_USERNAME")
password = os.getenv("PHISAVER_PASSWORD")

if not username or not password:
    print("Error: Set PHISAVER_USERNAME and PHISAVER_PASSWORD environment variables")
    exit(1)

# Step 1: Authenticate
print("Authenticating...")
auth_response = httpx.post(
    f"{base_url}/api/v1/login/",
    json={"email": username, "password": password},
)

if auth_response.status_code != 200:
    print(f"Authentication failed: {auth_response.status_code}")
    exit(1)

token = auth_response.json()["key"]
print("Authenticated\n")

# Define time range and timezone
AEST = ZoneInfo("Australia/Brisbane")
start_date = datetime(2025, 1, 1, tzinfo=AEST)
end_date = datetime(2025, 1, 7, tzinfo=AEST)

# Example 1: Get time series data for Production
print("=" * 60)
print("Fetching time series data...")
series_response = httpx.get(
    f"{base_url}/api/v1/ts/series/",
    headers={"Authorization": f"Token {token}"},
    params={
        "sites": "demo1",
        "start": start_date.isoformat(),
        "stop": end_date.isoformat(),
        "bin": "1d",  # Daily bins: 1d, 1h, 15min, etc.
        "mets": "Consumption,Production",  # Metrics: Production, Consumption, etc.
        "units": "W",  # Units: W, kW, kWh/day
    },
)

if series_response.status_code == 200:
    data = series_response.json()
    print("\nProduction data retrieved:")
    print(json.dumps(data, indent=4))
else:
    print(f"Failed: {series_response.status_code}")
    print(series_response.text)

# Example 2: Get data in table format (easier for analysis)
print("\n" + "=" * 60)
print("Fetching multiple sites with data in table format...")

table_response = httpx.get(
    f"{base_url}/api/v1/ts/table/",
    headers={"Authorization": f"Token {token}"},
    params={
        "sites": "demo1,demo2",  # Multiple devices
        "start": start_date.isoformat(),
        "stop": end_date.isoformat(),
        "units": "kWh/day",
    },
)

if table_response.status_code == 200:
    table_data = table_response.json()
    print("\nTable data retrieved:")
    for site, metrics in table_data.items():
        print(f"  Site: {site}")
        print(json.dumps(metrics, indent=4))
else:
    print(f"Failed: {table_response.status_code}")

# Example 3: Get multiple metrics by category
print("\n" + "=" * 60)
print("Fetching metrics by category (load)...")

multi_response = httpx.get(
    f"{base_url}/api/v1/ts/series/",
    headers={"Authorization": f"Token {token}"},
    params={
        "sites": "demo1",
        "start": start_date.isoformat(),
        "stop": end_date.isoformat(),
        "bin": "1d",
        "metcat": "load",  # Category: load, production, battery, etc.
        "units": "kWh/day",
    },
)

if multi_response.status_code == 200:
    multi_data = multi_response.json()
    print("\nMultiple metrics data retrieved:")
    print(json.dumps(multi_data, indent=4))
else:
    print(f"Failed: {multi_response.status_code}")

# Example 4: View the error response
print("\n" + "=" * 60)
print("Attempting to fetch data with invalid parameters...")

invalid_response = httpx.get(
    f"{base_url}/api/v1/ts/series/",
    headers={"Authorization": f"Token {token}"},
    params={
        "sites": "demo1",
        "start": start_date.isoformat(),
        "stop": end_date.isoformat(),
        "bin": "1h",
        "metcat": "InvalidMetric",  # Invalid metric category
        "units": "W",
    },
)

if invalid_response.status_code == 200:
    print("Data retrieved (unexpected!)")
else:
    print("OK: the expected error occurred.")
    print(f"Status: {invalid_response.status_code}")
    # View the error response by uncommenting the line below
    # print(invalid_response.text)
