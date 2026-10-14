"""
Authenticate with the PhiSaver API using httpx

This example shows how to exchange your email and password for API tokens:
a short-lived access token (15 minutes) and a refresh token (60 days).
Get demo credentials at https://phisaver.com
"""

import os
import sys

import httpx

# Load credentials from environment
base_url = os.getenv("PS_API_URL", "https://app.phisaver.com").rstrip("/")
username = os.getenv("PS_API_USERNAME")
password = os.getenv("PS_API_PASSWORD")

if not username or not password:
    print("Error: Set PS_API_USERNAME and PS_API_PASSWORD environment variables")
    sys.exit(1)

# Authenticate: POST email/password (JSON) to /api/v2/token/
response = httpx.post(
    f"{base_url}/api/v2/token/",
    json={"email": username, "password": password},
)

if response.status_code == httpx.codes.OK:
    tokens = response.json()
    print("Authentication successful!")
    print(f"Access token: {tokens['access'][:8]}... (valid for 15 minutes)")
    print("\nUse the access token in subsequent requests:")
    print('  headers = {"Authorization": "Bearer <access>"}')
    print("\nWhen it expires (401), get a new pair with the refresh token:")
    print('  httpx.post(f"{base_url}/api/v2/token/refresh/", json={"refresh": "<refresh>"})')
else:
    print(f"Authentication failed: {response.status_code}")
    print(response.text)
    sys.exit(1)
