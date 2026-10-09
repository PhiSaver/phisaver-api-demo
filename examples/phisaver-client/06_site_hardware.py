"""
Explore a site's metrics, switchboards, poles and IoTaWatts with the PhiSaver client

This example shows how to:
- List the metrics (circuits) a site reports, with their categories
- List switchboards, with the IoTaWatts and poles (circuit breakers) in each one
- List a site's IoTaWatt energy monitors and view one in detail
"""

from phisaver_client.api.iotawatts.iotawatts_retrieve import sync as get_iotawatt
from phisaver_client.api.sites.sites_iotawatts_list import sync as get_site_iotawatts
from phisaver_client.api.sites.sites_list import sync as get_sites
from phisaver_client.api.sites.sites_metrics_list import sync as get_metrics
from phisaver_client.api.sites.sites_switchboards_list import sync as get_switchboards
from phisaver_client.api.sites.sites_switchboards_poles_list import sync as get_poles
from phisaver_client.helpers import get_client_from_env

# Authenticate
client = get_client_from_env()

sites = get_sites(client=client)
if not sites:
    raise SystemExit("No sites available for this account")
# Prefer a site with configured metrics
site_id = next((s.id for s in sites if get_metrics(s.id, client=client)), sites[0].id)

# Metrics: the measured circuits, whose names you pass to `mets=` in time-series queries.
# Calculated metrics (Consumption, Import, Export, ...) are not listed but can still be queried.
print(f"Metrics for site '{site_id}':")
for metric in get_metrics(site_id, client=client):
    print(f"  {metric.id:<20} category={metric.category:<12} {metric.display_name}")

# Switchboards, with their IoTaWatts and poles
print(f"\nSwitchboards for site '{site_id}':")
switchboards = get_switchboards(site_id, client=client)
if not switchboards:
    print("  (none)")
for board in switchboards:
    print(f"  {board.name} ({board.id}): {board.pole_count} pole(s)")
    for iotawatt in board.iotawatts:
        print(f"    IoTaWatt {iotawatt.id}: {iotawatt.name}")
    for pole in get_poles(site_id, board.id, client=client):
        print(f"    pole {pole.id}: {pole.name} phase={pole.phase} current={pole.current}A")

# IoTaWatts at this site. For several sites use iotawatts_list.sync(client=client, site="site1,site2").
print(f"\nIoTaWatts at site '{site_id}':")
iotawatts = get_site_iotawatts(site_id, client=client)
if not iotawatts:
    print("  (none)")
for iotawatt in iotawatts:
    print(f"  {iotawatt.id}: {iotawatt.name}")

if iotawatts:
    detail = get_iotawatt(iotawatts[0].id, client=client)
    print(f"\nIoTaWatt '{detail.id}' details:")
    print(f"  Name: {detail.name}")
    print(f"  Switchboard: {detail.switchboard.name} ({detail.switchboard.id})")
    print(f"  VT model: {detail.vt_model}  phase: {detail.vt_phase}")
    print(f"  CTs: {len(detail.cts)}")
