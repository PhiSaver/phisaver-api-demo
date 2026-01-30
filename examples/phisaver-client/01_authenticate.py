"""
Authenticate with the PhiSaver API

This example shows different ways to authenticate with the PhiSaver API.
Get demo credentials at https://phisaver.com
"""

import os

from phisaver_client.helpers import get_client, get_client_from_env

# Method 1: Using environment variables (recommended over hardcoding)
# Set these in your environment (e.g., in your shell or .env file):
# PHISAVER_URL=https://app.phisaver.com
# PHISAVER_USERNAME=demo@example.com
# PHISAVER_PASSWORD=your_password

try:
    client = get_client_from_env()
    print("Authenticated using environment variables!")
except Exception as e:
    print(f"Authentication failed: {e}")
    print("Used the following environment variables:")
    print(f"PHISAVER_URL={os.getenv('PHISAVER_URL')}")
    print(f"PHISAVER_USERNAME={os.getenv('PHISAVER_USERNAME')}")
    print(f"PHISAVER_PASSWORD={'*' * len(os.getenv('PHISAVER_PASSWORD', ''))}")
