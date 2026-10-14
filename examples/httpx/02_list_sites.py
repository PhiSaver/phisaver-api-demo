"""
List sites using httpx

This example shows how to:
- List all sites your account can access
- Filter the site list
- Retrieve full details for one site
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

# Step 1: Authenticate and create a client that sends the token on every request
auth_response = httpx.post(f"{base_url}/api/v2/token/", json={"email": username, "password": password})
if auth_response.status_code != httpx.codes.OK:
    print(f"Authentication failed: {auth_response.status_code}")
    print(auth_response.text)
    sys.exit(1)

client = httpx.Client(
    base_url=base_url,
    headers={"Authorization": f"Bearer {auth_response.json()['access']}"},
    timeout=60,
)
print("Authenticated\n")

# Step 2: List sites
print("Fetching sites...")
sites_response = client.get("/api/v2/sites/")
sites_response.raise_for_status()
sites = sites_response.json()
print(f"Found {len(sites)} site(s)\n")

for site in sites:
    print(f"Site: {site['name']} ({site['id']})")
    print(f"  Status: {site['site_status']}  Data: {site['data_status']}  Solar: {site['solar_status']}")
    print(f"  Latest data: {site['last_data_at']}")

# Step 3: Filter sites (comma-separated values are accepted for id, data_status and solar_status)
if sites:
    prefix = sites[0]["name"][:2]
    filtered = client.get("/api/v2/sites/", params={"name_prefix": prefix}).json()
    print(f"\n{len(filtered)} site(s) have names starting with '{prefix}'")

    # Every list endpoint accepts id= with one id or comma-separated ids
    ids = ",".join(s["id"] for s in sites[:2])
    selected = client.get("/api/v2/sites/", params={"id": ids}).json()
    print(f"id={ids} returned {len(selected)} site(s)")

# Step 4: Get full details for one site
if sites:
    site_id = sites[0]["id"]
    print(f"\nFetching details for site '{site_id}'...")
    detail = client.get(f"/api/v2/sites/{site_id}/")
    detail.raise_for_status()
    print(json.dumps(detail.json(), indent=2))
