"""
Retrieve time-series energy data from PhiSaver API

This example shows how to:
- Get time-series data for specific metrics (e.g., Production, Consumption)
- Specify time ranges and binning intervals
- Access data in both series and table formats
- Handle multiple metrics and error responses
"""

from datetime import datetime
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
    pprint.pprint(series.parsed['demo1'], indent=4)



    
# Example 2: Get data in table format (easier for analysis)
print("\n" + "=" * 60)
print("Fetching multiple sites with data in table format...")
table = get_ts_table_detailed(
    sites=["demo1","demo2"],  # Multiple devices
    client=client,
    start=start_date,
    stop=end_date,
    units="kWh/day",
)

if table.parsed:
    print("\nTable data retrieved:")
    for site in table.parsed.additional_keys:
        print(f"  Site: {site}")
        pprint.pprint(table.parsed[site], indent=4)
    
# Example 3: Get multiple metrics
print("\n" + "=" * 60)

multi_series = get_ts_series_detailed(
    sites=["demo1"],
    client=client,
    start=start_date,
    stop=end_date,
    bin_="1d",  
    metcat=["load"], 
    units="kWh/day",
)

if multi_series.parsed:
    print("\nMultiple metrics data retrieved:")
    pprint.pprint(multi_series.parsed['demo1'], indent=4)
else:
    print("No data retrieved: ", multi_series)
        
# Example 4: View the error
print("\n" + "=" * 60)
print("Attempting to fetch data with invalid parameters...")
invalid_series = get_ts_series_detailed(
    sites=["demo1"],
    client=client,
    start=start_date,
    stop=end_date,
    bin_="1h",  
    metcat=["InvalidMetric"],  # Invalid metric
    units="W",
)
if invalid_series.parsed:
    print("Data retrieved (unexpected!)")
else:
    print("OK: the expected error occurred.")
    # View the response by uncommenting the line below.")
    # pprint.pprint(invalid_series)     
    