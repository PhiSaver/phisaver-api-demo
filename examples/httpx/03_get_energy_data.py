"""
Retrieve time-series energy data using httpx

This example shows how to fetch time-series energy data using raw httpx.
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

# Step 2: Define time range
AEST = ZoneInfo("Australia/Brisbane")
start_date = datetime(2025, 1, 1, tzinfo=AEST)
end_date = datetime(2025, 1, 7, tzinfo=AEST)

# Step 3: Get time series data
print("Fetching solar production data...")
series_response = httpx.get(
    f"{base_url}/api/v1/ts/series/",
    headers={"Authorization": f"Token {token}"},
    params={
        "sites": "demo1",
        "start": start_date.isoformat(),
        "stop": end_date.isoformat(),
        "bin": "1d",  # Daily bins
        "mets": "Consumption,Production",  # Comma-separated metrics
        "units": "W",
    },
)

if series_response.status_code != 200:
    print(f"Failed to fetch data: {series_response.status_code}")
    print(series_response.text)
    exit(1)

data = series_response.json()
print("Data retrieved\n")
print(json.dumps(data, indent=2))

# Step 4: Process and display the data
print("\n" + "=" * 60)
print("Processing data...")

for site, metrics in data.items():
    print(f"\nSite: {site}")
    for metric_name, values in metrics.items():
        print(f"  {metric_name}:")
        for timestamp, value in values:
            if value is not None:
                print(f"    {timestamp}: {value:.2f} W")

# Step 5: Get table format data
print("\n" + "=" * 60)
print("Fetching data in table format...")

table_response = httpx.get(
    f"{base_url}/api/v1/ts/table/",
    headers={"Authorization": f"Token {token}"},
    params={
        "sites": "demo1",
        "start": start_date.isoformat(),
        "stop": end_date.isoformat(),
        "units": "kWh/day",
    },
)

if table_response.status_code == 200:
    table_data = table_response.json()
    print("Table data retrieved")
    print(json.dumps(table_data, indent=2)[:500] + "...")
else:
    print(f"Failed: {table_response.status_code}")

# Step 6: Get multiple metrics with hourly bins
print("\n" + "=" * 60)
print("Fetching multiple metrics (hourly)...")

multi_response = httpx.get(
    f"{base_url}/api/v1/ts/series/",
    headers={"Authorization": f"Token {token}"},
    params={
        "sites": "demo1",
        "start": start_date.isoformat(),
        "stop": end_date.isoformat(),
        "bin": "1h",  # Hourly bins
        "mets": "Production,Consumption,FeedIn",
        "units": "W",
    },
)

if multi_response.status_code == 200:
    multi_data = multi_response.json()
    print("Multi-metric data retrieved\n")
    
    for site, metrics in multi_data.items():
        print(f"Site: {site}")
        for metric_name, values in metrics.items():
            # Calculate average
            valid_values = [v for ts, v in values if v is not None]
            if valid_values:
                avg_value = sum(valid_values) / len(valid_values)
                print(f"  {metric_name}: {len(values)} readings, avg = {avg_value:.2f} W")
else:
    print(f"Failed: {multi_response.status_code}")
