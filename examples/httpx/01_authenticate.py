"""
Authenticate with the PhiSaver API using httpx

This example shows how to authenticate and get an auth token using raw httpx.
Get demo credentials at https://phisaver.com
"""

import os
import httpx

# Load credentials from environment
base_url = os.getenv("PHISAVER_URL", "https://app.phisaver.com")
username = os.getenv("PHISAVER_USERNAME")
password = os.getenv("PHISAVER_PASSWORD")

if not username or not password:
    print("Error: Set PHISAVER_USERNAME and PHISAVER_PASSWORD environment variables")
    exit(1)

# Authenticate
auth_url = f"{base_url}/api/v1/login/"
response = httpx.post(
    auth_url,
    json={"email": username, "password": password},
)

if response.status_code == 200:
    token = response.json()["key"]
    print("Authentication successful!")
    print(f"Token: {token[:20]}...")
    print(f"\nUse this token in subsequent requests:")
    print(f'  headers = {{"Authorization": "Token {token}"}}')
else:
    print(f"Authentication failed: {response.status_code}")
    print(response.text)
