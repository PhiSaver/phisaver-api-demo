# PhiSaver Client Library Examples

These examples demonstrate using the `phisaver-client` Python library - an auto-generated client with type hints and IDE autocomplete support.

## Prerequisites

See the [main README](../../README.md#authentication) for credentials and authentication details.

## Installation

Probably you want to use a virtual environment (venv, uv, conda, etc.), but that's not required.

```bash
pip install "phisaver-client>=2.1"
```

Version 2.x of the client targets the v2 API (`/api/v2/`). These examples need 2.1 or later. Version 1.x targets the retired v1 API.

## Usage

Set your credentials as environment variables (see [.env.example](../../.env.example)):

```bash
export PS_API_URL="https://app.phisaver.com"
export PS_API_USERNAME="demo@phisaver.com"
export PS_API_PASSWORD="checkthewebsiteoremailsupport"
```

Then run the examples:

```bash
python examples/phisaver-client/01_authenticate.py
python examples/phisaver-client/02_list_sites.py
python examples/phisaver-client/03_get_energy_data.py
python examples/phisaver-client/04_heatmap.py
python examples/phisaver-client/05_fleets.py
python examples/phisaver-client/06_site_hardware.py
```

The examples discover which sites your account can access, so they work with any account.

## Examples

- [01_authenticate.py](01_authenticate.py) - Authenticate and get a client instance
- [02_list_sites.py](02_list_sites.py) - List, filter and retrieve sites
- [03_get_energy_data.py](03_get_energy_data.py) - Fetch time-series and table energy data
- [04_heatmap.py](04_heatmap.py) - Fetch heatmap (date x time-of-day) data
- [05_fleets.py](05_fleets.py) - List fleets and query every site in a fleet
- [06_site_hardware.py](06_site_hardware.py) - Metrics, switchboards, poles and a site's IoTaWatts
- [10_authenticate_alternative.py](10_authenticate_alternative.py) - Hard-coded credentials (not recommended)

## Tips

**Pass lists as comma-separated strings.** Parameters such as `sites` and `mets` take one string:

```python
get_ts_series(client=client, sites="site1,site2", mets="Consumption,Production", bin_="1d")
```

Passing a Python list (`mets=["Consumption", "Production"]`) sends the parameter twice, which the API rejects with 400.

**Errors raise `UnexpectedStatus`.** Clients from `get_client()` and `get_client_from_env()` raise `phisaver_client.errors.UnexpectedStatus` for any error response (400, 403, 404, 500, ...). The exception has `.status_code` and `.content`, which names the invalid parameters:

```python
from phisaver_client import errors

try:
    series = get_ts_series(client=client, sites="site1", metcat="bogus", bin_="1h", duration="1d")
except errors.UnexpectedStatus as e:
    print(e.status_code, e.content.decode())
```

**`sync` vs `sync_detailed`.** Each endpoint module has `sync(...)`, which returns the parsed model, and `sync_detailed(...)`, which returns a `Response` with `.status_code`, `.content` and `.parsed`. To check status codes yourself instead of catching exceptions, create the client with `get_client_from_env(raise_on_unexpected_status=False)`; `sync()` then returns `None` on error.

**Time-series responses** support dict-style access and `.to_dict()`:

```python
series = get_ts_series(client=client, sites="site1", mets="Net", bin_="1h", start=start, stop=stop)
points = series["site1"].to_dict()["Net"]  # [[timestamp, value], ...]
```

## About This Client

The `phisaver-client` library is **automatically generated** from the PhiSaver API's [OpenAPI specification](../../schema.yml) using [openapi-python-client](https://github.com/openapi-generators/openapi-python-client).

## Other Languages

The OpenAPI specification can generate clients for many languages. The [OpenAPI Generator](https://openapi-generator.tech/) has a complete list of supported languages.
