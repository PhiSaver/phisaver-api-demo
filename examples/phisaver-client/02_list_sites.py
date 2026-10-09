"""
List and retrieve site information from PhiSaver API

This example demonstrates how to:
- Get a list of all sites your account can access
- Filter the site list
- Retrieve details for a specific site (rates, location, metrics, switchboards)
"""

from phisaver_client.api.sites.sites_list import sync as get_sites
from phisaver_client.api.sites.sites_retrieve import sync as get_site
from phisaver_client.helpers import get_client_from_env

# Authenticate
client = get_client_from_env()

# Get all sites
print("Fetching all sites...")
sites = get_sites(client=client)

print(f"\nFound {len(sites)} site(s):\n")
for site in sites:
    print(f"  {site.name} ({site.id})")
    print(f"    Status: {site.site_status}  Data: {site.data_status}  Solar: {site.solar_status}")
    print(f"    Latest data: {site.last_data_at}")
    print()

# Filter sites, e.g. by name prefix (id, data_status, solar_status also accept comma-separated values)
if sites:
    prefix = sites[0].name[:2]
    filtered = get_sites(client=client, name_prefix=prefix)
    print(f"{len(filtered)} site(s) have names starting with '{prefix}'")

    # Every list endpoint accepts id= with one id or comma-separated ids
    ids = ",".join(s.id for s in sites[:2])
    selected = get_sites(client=client, id=ids)
    print(f"id={ids} returned {len(selected)} site(s)\n")

# Get a specific site by id
if sites:
    site_id = sites[0].id
    print(f"Fetching detailed info for site '{site_id}'...")
    site = get_site(site_id, client=client)

    print("\nSite Details:")
    print(f"  Name: {site.name}")
    print(f"  ID: {site.id}")
    print(f"  Solar Status: {site.solar_status}")
    print(f"  Battery: {site.battery}")
    print(f"  Timezone: {site.timezone}")
    print(f"  Rates: import={site.rates.import_rate} export={site.rates.export_rate} service={site.rates.service_rate}")
    if site.metrics:
        print(f"  Metrics available: {', '.join(m.id for m in site.metrics)}")
    if site.switchboards:
        print(f"  Switchboards: {', '.join(sb.name for sb in site.switchboards)}")
    if site.actions:
        print(f"  Actions: {', '.join(a.name for a in site.actions)}")
    if site.images:
        print(f"  Images available: {len(site.images)}")
