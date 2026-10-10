"""
Authenticate with hard-coded credentials (not recommended!)

Prefer environment variables; see 01_authenticate.py.
"""

import httpx
from phisaver_client.helpers import get_client

# Direct username/password (not recommended!)
url = "https://app.phisaver.com/"
username = "username@example.com"
password = "your_password"

try:
    client = get_client(
        base_url=url,
        username=username,
        password=password,
        verify_ssl=True,  # Set to False if testing locally with a self-signed certificate
    )
    print("Authenticated using hard-coded variables!")
except httpx.HTTPError as e:
    print(f"Authentication failed: {e}")
    print("Check the hard-coded credentials in the script.")
