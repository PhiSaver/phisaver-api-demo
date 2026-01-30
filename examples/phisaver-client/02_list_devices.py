"""
List and retrieve device information from PhiSaver API

This example demonstrates how to:
- Get a list of all devices
- Retrieve details for a specific device
- Access device properties like solar capacity, location, and metrics
"""

from phisaver_client.api.devices.devices_list import sync as get_devices
from phisaver_client.api.devices.devices_retrieve import sync as get_device
from phisaver_client.helpers import get_client_from_env

# Authenticate
client = get_client_from_env()

# Get all devices
print("Fetching all devices...")
devices = get_devices(client=client)

print(f"\nFound {len(devices)} device(s):\n")
for device in devices:
    print(f"  {device.name} ({device.ref})")
    print(f"    ID: {device.id}")
    print(f"    Solar: {device.solar}")
    
    if device.latest:
        print(f"    Latest data: {device.latest}")
    print(f"    Timezone: {device.timezone}")
    print()

# Get a specific device by reference
if devices:
    device_ref = devices[0].ref
    print(f"Fetching detailed info for device '{device_ref}'...")
    device = get_device(device_ref, client=client)

    print("\nDevice Details:")
    print(f"  Name: {device.name}")
    print(f"  Reference: {device.ref}")
    print(f"  Solar Status: {device.solar}")
    print(f"  Rates: {device.rates}")
    print(f"  Timezone: {device.timezone}")
    if device.metrics:
        print(f"  Metrics available: {', '.join(device.metrics)}")
    

    if device.images:
        print(f"  Images available: {len(device.images)}")
        print(f"    First image: https://phisaver.com{device.images[0]}")
