"""
Explore a site's metrics, switchboards, poles and IoTaWatts using httpx

This example shows how to:
- List the metrics (circuits) a site reports, with their categories
- List switchboards, with the IoTaWatts and poles (circuit breakers) in each one
- List a site's IoTaWatt energy monitors and view one in detail
"""

import json
import os
import sys

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

sites = client.get("/api/v2/sites/").json()
if not sites:
    print("No sites available for this account")
    sys.exit(1)
# Prefer a site with configured metrics
site_id = next(
    (s["id"] for s in sites[:3] if client.get(f"/api/v2/sites/{s['id']}/metrics/").json()),
    sites[0]["id"],
)

# Metrics: the measured circuits, whose names you pass to `mets=` in time-series queries.
# Calculated metrics (Consumption, Import, Export, ...) are not listed but can still be queried.
print(f"Metrics for site '{site_id}':")
for metric in client.get(f"/api/v2/sites/{site_id}/metrics/").json():
    print(f"  {metric['id']:<20} category={metric['category']:<12} {metric['display_name']}")

# Switchboards, with their IoTaWatts and poles
print(f"\nSwitchboards for site '{site_id}':")
switchboards = client.get(f"/api/v2/sites/{site_id}/switchboards/").json()
if not switchboards:
    print("  (none)")
for board in switchboards[:2]:
    print(f"  {board['name']} ({board['id']}): {board['pole_count']} pole(s)")
    for iotawatt in board["iotawatts"]:
        print(f"    IoTaWatt {iotawatt['id']}: {iotawatt['name']}")
    poles = client.get(f"/api/v2/sites/{site_id}/switchboards/{board['id']}/poles/").json()
    for pole in poles:
        print(f"    pole {pole['id']}: {pole['name']} phase={pole.get('phase')} current={pole.get('current')}A")

# IoTaWatts at this site. For several sites use /api/v2/iotawatts/?site=site1,site2
print(f"\nIoTaWatts at site '{site_id}':")
iotawatts = client.get(f"/api/v2/sites/{site_id}/iotawatts/").json()
if not iotawatts:
    print("  (none)")
for iotawatt in iotawatts:
    print(f"  {iotawatt['id']}: {iotawatt['name']}")

if iotawatts:
    iotawatt_id = iotawatts[0]["id"]
    print(f"\nIoTaWatt '{iotawatt_id}' details:")
    print(json.dumps(client.get(f"/api/v2/iotawatts/{iotawatt_id}/").json(), indent=2)[:2000])
