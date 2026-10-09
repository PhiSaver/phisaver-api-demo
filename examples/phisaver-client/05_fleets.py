"""
List fleets and query a whole fleet with the PhiSaver client

A fleet is a named group of sites. Any time-series query accepts
`fleet=<id>` in place of `sites="site1,site2,..."`.
"""

import pprint
from datetime import datetime, timedelta

from phisaver_client.api.fleets.fleets_list import sync as get_fleets
from phisaver_client.api.fleets.fleets_retrieve import sync as get_fleet
from phisaver_client.api.ts.ts_table_retrieve import sync as get_ts_table
from phisaver_client.helpers import get_client_from_env

# Authenticate
client = get_client_from_env()

# List fleets
fleets = get_fleets(client=client)
print(f"Found {len(fleets)} fleet(s)")
for fleet in fleets:
    print(f"  {fleet.name} ({fleet.id}): {fleet.site_count} site(s), timezone {fleet.timezone}")

if not fleets:
    raise SystemExit("This account has no fleets.")

# Fleet details include its sites
fleet = get_fleet(fleets[0].id, client=client)
print(f"\nFleet '{fleet.id}' sites:")
for site in fleet.sites:
    print(f"  {site.name} ({site.id})")

# Daily energy for every site in the fleet, last 30 days
end_date = datetime.now().astimezone()
start_date = end_date - timedelta(days=30)
table = get_ts_table(
    client=client,
    fleet=fleet.id,  # Equivalent to sites=<every site in the fleet>
    start=start_date,
    stop=end_date,
    mets="Production,Consumption",
    units="kWh/day",
)
print("\nFleet table:")
pprint.pprint(table.to_dict(), indent=4)
