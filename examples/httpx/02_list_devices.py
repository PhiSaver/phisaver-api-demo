"""
List devices using httpx

This example shows how to retrieve device information using raw httpx.
"""

import os
import httpx
import json

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
    print(auth_response.text)
    exit(1)

token = auth_response.json()["key"]
print("Authenticated\n")

# Step 2: List devices
print("Fetching devices...")
devices_response = httpx.get(
    f"{base_url}/api/v1/devices/",
    headers={"Authorization": f"Token {token}"},
)

if devices_response.status_code != 200:
    print(f"Failed to fetch devices: {devices_response.status_code}")
    print(devices_response.text)
    exit(1)

devices = devices_response.json()
print(f"Found {len(devices)} device(s)\n")

# Display device information
for device in devices:
    print(f"Device: {device['name']} ({device['ref']})")
    print(f"  ID: {device['id']}")
    print(f"  Solar: {device.get('solar', 'N/A')}")
    print(f"  Timezone: {device.get('timezone', 'N/A')}")
    if device.get('latest'):
        print(f"  Latest data: {device['latest']}")
    print()

# Step 3: Get specific device details
if devices:
    device_ref = devices[0]['ref']
    print(f"Fetching details for device '{device_ref}'...")
    
    device_response = httpx.get(
        f"{base_url}/api/v1/devices/{device_ref}/",
        headers={"Authorization": f"Token {token}"},
    )
    
    if device_response.status_code == 200:
        device = device_response.json()
        print(f"Device details:")
        print(json.dumps(device, indent=2))
    else:
        print(f"Failed: {device_response.status_code}")
