"""
Retrieve time-series energy data from PhiSaver API

This example shows how to:
- Get time-series data for specific metrics (e.g., Production, Consumption)
- Specify time ranges and binning intervals
- Access data in both series and table formats
- Query metrics by category
- Handle error responses

Note: list-like parameters (sites, mets) are ONE comma-separated string,
e.g. mets="Consumption,Production". Do not pass a Python list.
"""

import pprint
from datetime import datetime, timedelta

from phisaver_client import errors
from phisaver_client.api.sites.sites_list import sync as get_sites
from phisaver_client.api.sites.sites_metrics_list import sync as get_metrics
from phisaver_client.api.ts.ts_series_retrieve import sync as get_ts_series
from phisaver_client.api.ts.ts_table_retrieve import sync as get_ts_table
from phisaver_client.helpers import get_client_from_env

# Authenticate. Any error response raises errors.UnexpectedStatus (see Example 4).
client = get_client_from_env()

# Pick sites to query. Prefer a site with configured metrics
# (needed for metcat queries), plus a second site for the multi-site table.
sites = get_sites(client=client)
if not sites:
    raise SystemExit("No sites available for this account")
site = next((s for s in sites if get_metrics(s.id, client=client)), sites[0])
site_id = site.id
site_ids = [site_id, *[s.id for s in sites if s.id != site_id][:1]]

# Time range: the 30 days before the site's latest data
# last_data_at is None if the site has never reported data
end_date = site.last_data_at or datetime.now().astimezone()
start_date = end_date - timedelta(days=30)
print(f"Querying {site_ids} from {start_date.isoformat()} to {end_date.isoformat()}")

# Example 1: Get time series data for two metrics
series = get_ts_series(
    client=client,
    sites=site_id,
    start=start_date,
    stop=end_date,
    bin_="1d",  # Daily bins: 1d, 1h, 15min, etc.
    mets="Consumption,Production",  # Metrics: Production, Consumption, Net, etc.
    units="W",  # Units: W, kW, kWh/day, $/day
)

# series[site][metric] -> [[timestamp, value], ...]
print("\nSeries data retrieved:")
pprint.pprint(series[site_id].to_dict(), indent=4)

# Example 2: Get data in table format (one value per metric; easier for analysis)
print("\n" + "=" * 60)
print("Fetching multiple sites with data in table format...")
table = get_ts_table(
    client=client,
    sites=",".join(site_ids),  # Multiple sites
    start=start_date,
    stop=end_date,
    units="kWh/day",
)

print("\nTable data retrieved:")
for site in table.additional_keys:
    print(f"  Site: {site}")
    pprint.pprint(table[site].to_dict(), indent=4)

# Example 3: Get all metrics in a category
print("\n" + "=" * 60)
multi_series = get_ts_series(
    client=client,
    sites=site_id,
    start=start_date,
    stop=end_date,
    bin_="1d",
    metcat="load",  # Category: load, production, battery, net, calc, other, all
    units="kWh/day",
)

print("\nMetrics by category retrieved:")
pprint.pprint(multi_series[site_id].to_dict(), indent=4)

# Example 4: View the error
print("\n" + "=" * 60)
print("Attempting to fetch data with invalid parameters...")
try:
    get_ts_series(
        client=client,
        sites=site_id,
        start=start_date,
        stop=end_date,
        bin_="1h",
        metcat="InvalidMetric",  # Invalid metric category
        units="W",
    )
    print("Data retrieved (unexpected!)")
except errors.UnexpectedStatus as e:
    print("OK: the expected error occurred.")
    print(f"Status: {e.status_code}")
    print(e.content.decode())  # Names the invalid parameters
