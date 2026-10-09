"""
Authenticate with the PhiSaver API

This example shows how to get an authenticated client from environment variables.
Get demo credentials at https://phisaver.com
"""

import os

from phisaver_client.helpers import get_client_from_env

# Using environment variables (recommended over hardcoding)
# Set these in your environment (e.g., in your shell or .env file):
# PS_API_URL=https://app.phisaver.com
# PS_API_USERNAME=demo@phisaver.com
# PS_API_PASSWORD=your_password

try:
    client = get_client_from_env()
    print("Authenticated using environment variables!")
except Exception as e:
    print(f"Authentication failed: {e}")
    print("Used the following environment variables:")
    print(f"PS_API_URL={os.getenv('PS_API_URL')}")
    print(f"PS_API_USERNAME={os.getenv('PS_API_USERNAME')}")
    print(f"PS_API_PASSWORD={'*' * len(os.getenv('PS_API_PASSWORD', ''))}")
    raise SystemExit(1)
