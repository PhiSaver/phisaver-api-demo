"""
Authenticate with the PhiSaver API using httpx

This example shows how to exchange a username and password for an API token.
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

# Authenticate: POST username/password (form-encoded) to /api/v2/token/
response = httpx.post(
    f"{base_url}/api/v2/token/",
    data={"username": username, "password": password},
)

if response.status_code == 200:
    token = response.json()["token"]
    print("Authentication successful!")
    print(f"Token: {token[:8]}...")
    print("\nUse this token in subsequent requests:")
    print('  headers = {"Authorization": "Token <token>"}')
else:
    print(f"Authentication failed: {response.status_code}")
    print(response.text)
    sys.exit(1)
