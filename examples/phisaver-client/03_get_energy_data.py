"""
Retrieve time-series energy data from PhiSaver API

This example shows how to:
- Get time-series data for specific metrics (e.g., Production, Consumption)
- Specify time ranges and binning intervals
- Access data in both series and table formats
"""

from datetime import datetime
import json
import pprint
from zoneinfo import ZoneInfo

from phisaver_client.api.ts.ts_series_retrieve import sync_detailed as get_ts_series_detailed
from phisaver_client.api.ts.ts_table_retrieve import sync_detailed as get_ts_table_detailed
from phisaver_client.helpers import get_client_from_env

# Authenticate
client = get_client_from_env()

# Define time range and timezone
AEST = ZoneInfo("Australia/Brisbane")
start_date = datetime(2025, 1, 1, tzinfo=AEST)
end_date = datetime(2025, 1, 7, tzinfo=AEST)

# Example 1: Get time series data for Production
print("Fetching solar production data...")
series = get_ts_series_detailed(
    sites=["demo1"],  # Replace with actual device ref
    client=client,
    start=start_date,
    stop=end_date,
    bin_="1d",  # Daily bins: 1d, 1h, 15min, etc.
    mets=["Consumption","Production"],  # Metrics: Production, Consumption, etc.
    units="W",  # Units: W, Wh, kWh
)

# series contains raw and parsed data. 
# Use series.parsed for easy access.
if series.parsed:
    print("\nProduction data retrieved:") 
    print(json.dumps(series.parsed, indent=4))



    
# Example 2: Get data in table format (easier for analysis)
print("\n" + "=" * 60)
print("Fetching data in table format...")
table = get_ts_table_detailed(
    sites=["demo_device_01", "demo_device_02"],  # Multiple devices
    client=client,
    start=start_date,
    stop=end_date,
    units="kWh/day",
)

if table.parsed:
    print(f"\nTable data retrieved:")
    for site, data in table.parsed.items():
        print(f"\n  Site: {site}")
        print(f"    Data type: {type(data)}")
        # Table format typically includes timestamps and all available metrics

# Example 3: Get multiple metrics
print("\n" + "=" * 60)
print("Fetching multiple metrics...")
multi_series = get_ts_series_detailed(
    sites=["demo_device_01"],
    client=client,
    start=start_date,
    stop=end_date,
    bin_="1h",  # Hourly data
    mets=["Production", "Consumption", "FeedIn"],
    units="W",
)

if multi_series.parsed:
    for site, metrics in multi_series.parsed.items():
        print(f"\n  Site: {site}")
        for metric_name, values in metrics.items():
            if values:
                avg_value = sum(v[1] for v in values if v[1]) / len([v for v in values if v[1]])
                print(f"    {metric_name}: {len(values)} readings, avg = {avg_value:.2f} W")
