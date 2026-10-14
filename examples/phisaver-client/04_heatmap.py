"""
Retrieve heatmap data from PhiSaver API

The heatmap endpoint returns [day_of_year, hour, value] points for one site, convenient for plotting
time-of-day vs day patterns. Heatmap values are always in Watts.
"""

from datetime import datetime, timedelta

from phisaver_client.api.sites.sites_list import sync as get_sites
from phisaver_client.api.ts.ts_heatmap_retrieve import sync as get_heatmap
from phisaver_client.helpers import get_client_from_env

# Authenticate
client = get_client_from_env()

# Pick the first site and the 7 days before its latest data
sites = get_sites(client=client)
if not sites:
    raise SystemExit("No sites available for this account")
site = sites[0]
# last_data_at is None if the site has never reported data
end_date = site.last_data_at or datetime.now().astimezone()
start_date = end_date - timedelta(days=7)

print(f"Fetching heatmap for '{site.id}'...")
heatmap = get_heatmap(
    client=client,
    sites=site.id,
    start=start_date,
    stop=end_date,
    mets="Net",  # One or more comma-separated metrics
)

# Response shape: {site: {metric: [[day_of_year (1-365), hour (0-23), watts], ...]}}
for site_id, metrics in heatmap.to_dict().items():
    for metric, points in metrics.items():
        print(f"{site_id} / {metric}: {len(points)} points")
        for point in points[:5]:
            print(f"  {point}")
