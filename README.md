# Phisaver API Usage

This folder contains sample code and documentation for using the PhiSaver API (v2).

PhiSaver provides secure access to private energy data for residential and commercial solar installations. This document shows developers and researchers how to retrieve site information and time-series energy data.

The API is described by a [schema](schema.yml) using the OpenAPI v3 specification. All endpoints live under `/api/v2/`. See [Migrating from v1](#migrating-from-v1) if you used the earlier API.

*Three* methods are documented to interact with the API:
1. Command-line HTTP 
2. Direct HTTP requests using Python 
3. Python client library using [phisaver-client](https://pypi.org/project/phisaver-client/)

For advanced users, OpenAPI clients can be auto-generated for other languages. The phisaver-client, above, is the reference example. 

## Authentication

The API requires authentication for all requests. 

Existing users can use their email and password to access their data. Exchange them for a token at `POST /api/v2/token/`, then send `Authorization: Token <token>` on every request.

The demo account has an *unchanging* token for convenience. Production accounts will have rotating tokens.

**Demo Credentials**:
- **URL**: `https://app.phisaver.com`
- **Username**: `demo@phisaver.com`
- **Password**: `checkthewebsiteoremailsupport`


## Quick Start

The quickest way to explore the API is using [HTTPie](https://httpie.io/), a user-friendly command-line HTTP client. You could also use `curl` or `wget`. 

```bash
# Install HTTPie
apt install httpie  # Linux (use brew on mac, or pip, and refer to note re certificates in FAQ)


# Set credentials as environment variables
export PS_API_URL="https://app.phisaver.com"
export PS_API_USERNAME="your_email@example.com"
export PS_API_PASSWORD="your_password"

# Authenticate and save token 
export TOKEN=$(http -f POST $PS_API_URL/api/v2/token/ \
  username="$PS_API_USERNAME" \
  password="$PS_API_PASSWORD" \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['token'])")

# List the sites you can access (note each site's "id")
http GET $PS_API_URL/api/v2/sites/ "Authorization:Token $TOKEN"

# Get time-series energy data 
http GET $PS_API_URL/api/v2/ts/series/ \
  "Authorization:Token $TOKEN" \
  sites==demo1 \
  start=="2025-01-01T00:00:00+10:00" \
  stop=="2025-01-07T00:00:00+10:00" \
  bin==1d \
  mets==Production \
  units==kWh/day 
```

## Three Ways to Interact with the PhiSaver API

### 1. HTTPie (Command Line)

**Best for**: Quick exploration, debugging, shell scripts, learning the API

HTTPie is a simple, intuitive command-line HTTP client with JSON, sessions and colorized output. 

**Installation:**
```bash
brew install httpie  # macOS
apt install httpie   # Linux (see FAQ re certificates below)
pip install httpie   # Python
```

More:
- [HTTPie README](examples/httpie/README.md)

---

### 2. Python + httpx

**Best for**: Production applications, async/await support, HTTP/2, custom integrations

Direct HTTP requests using the modern `httpx` library without the generated client wrapper.

**Installation:**
```bash
pip install httpx
```

More:
- [httpx examples](examples/httpx/)

---

### 3. Python + phisaver-client

**Best for**: Type-safe Python applications, IDE autocomplete, generated from OpenAPI spec

Auto-generated Python client library with type hints and full API coverage. Version 2.x targets the v2 API; these examples need 2.1 or later.

**Installation:**
```bash
pip install "phisaver-client>=2.1"
```
More:
- [phisaver-client README](examples/phisaver-client/README.md)
- [phisaver-client examples](examples/phisaver-client/) 

## Endpoints

All endpoints are read-only `GET` requests unless noted.

| Endpoint | Description |
|---|---|
| `POST /api/v2/token/` | Exchange `username` + `password` for a token |
| `/api/v2/sites/` | Sites you can access (filter: `id`, `name_prefix`, `data_status`, `solar_status`) |
| `/api/v2/sites/{id}/` | Site detail: timezone, location, rates, metrics, switchboards, images |
| `/api/v2/sites/{site_id}/metrics/` | Measured circuits at a site, with display name and category |
| `/api/v2/sites/{site_id}/switchboards/` | Switchboards at a site, with their IoTaWatts |
| `/api/v2/sites/{site_id}/switchboards/{id}/poles/` | Poles (circuit breakers) in a switchboard |
| `/api/v2/sites/{site_id}/iotawatts/` | IoTaWatts at a site (same as `/api/v2/iotawatts/?site={site_id}`) |
| `/api/v2/fleets/`, `/api/v2/fleets/{id}/` | Named groups of sites |
| `/api/v2/iotawatts/`, `/api/v2/iotawatts/{id}/` | IoTaWatt energy monitors, with CTs and voltage reference (filter: `site`) |

Every list endpoint accepts `id` (one id, or comma-separated ids) to return only those items, e.g. `/api/v2/fleets/?id=fleet1,fleet2`.
| `/api/v2/ts/series/` | Time-series data `[[timestamp, value], ...]` |
| `/api/v2/ts/table/` | One aggregated value per metric (no timestamps) |
| `/api/v2/ts/heatmap/` | `[[day_of_year, hour, watts], ...]` for time-of-day plots (one site) |

## API Details

The examples given use httpie, but the same parameters apply to all methods of interacting with the API. Check the FAQ about '==' syntax in HTTPie. The [Cheat Sheet](CHEATSHEET.md) lists every parameter.

### Time Ranges

**Input formats:**
- **ISO8601** (recommended): `2025-01-01T00:00:00+10:00` - includes timezone
- **Epoch seconds**: `1735668000` - Unix timestamp
- **Duration**: Use `duration` instead of `start` (e.g., `duration=7d`). The range ends at `stop`, or now if `stop` is omitted

**Output formats** (use `timeformat` parameter):
- `iso` (default): `2025-01-01T00:00:00+10:00`
- `epoch`: `1735668000` - Unix timestamp in seconds
- `epochms`: `1735668000000` - Unix timestamp in milliseconds

**Example:**
```bash
# ISO8601 input (recommended)
start=="2025-01-01T00:00:00+10:00" stop=="2025-01-07T00:00:00+10:00"

# Epoch input
start==1735668000 stop==1736272800

# The last 7 days, ending now
duration==7d

# Output as epoch milliseconds
timeformat==epochms
```

### Sites

Query single or multiple sites using the `sites` parameter with site ids from `/api/v2/sites/`:

**Single site:**
```bash
sites==demo1
```

**Multiple sites** (one comma-separated value - do not repeat the parameter):
```bash
sites==demo1,demo2,demo3
```

**Fleet (predefined groups):**
```bash
fleet==myfleet  # Equivalent to sites==site1,site2,site3
```

### Metrics and Circuits

**Select metrics** using `mets` parameter. A site's measured circuits, with display names and categories, are listed at `/api/v2/sites/{id}/metrics/`. Calculated metrics (`Consumption`, `Import`, `Export`, `FreeConsumption`, `ImportConsumption`, `Unmonitored`, `BatteryCharge`, `BatteryDischarge`) are not listed there but can be queried at any site.
```bash
# Single metric
mets==Production

# Multiple metrics
mets==Production,Consumption,Net
```

**Filter by category** using `metcat` parameter:
- `load` - Consumption circuits (every metric not listed below)
- `production` - Solar: `Production`
- `battery` - `Battery`, `BatteryCharge`, `BatteryDischarge`
- `net` - Grid: `Net`, `Import`, `Export`
- `calc` - Calculated: `Consumption`, `FreeConsumption`, `ImportConsumption`, `Unmonitored`
- `other` - Other circuits
- `all` - Every metric

Each metric belongs to exactly one category.

**Example:**
```bash
# Get all consumption circuits
metcat==load

# Get grid metrics (Net, Import, Export)
metcat==net

# Get specific circuits by name
mets==Production,AirConditioner,HotWater
```

### Units

Units differ between between power (Watts) and energy (kWh) data. Where data is 'binned' into intervals (e.g., daily totals), the average of that interval is returned by default.

**Common units:**
- `W` (recommended) - Instantaneous power in watts 
- `kWh/day` (recommended) - Energy per day
- `kW` - Instantaneous power in kilowatts
- `$/day` - Cost per day with tariff applied

`/ts/heatmap/` always returns `W`.

**Example:**
```bash
# Time-series with instantaneous power
/api/v2/ts/series/ ... units==W

# Table with daily energy
/api/v2/ts/table/ ... units==kWh/day
```

### Binning

Group data into time intervals using the `bin` parameter (required for `/ts/series/`, not used elsewhere):

**Common bins:**
- `1h` - Hourly
- `1d` - Daily
- `1ME` - Month-end
- `1W` - Weekly

**Example:**
```bash
# Hourly data for one day
bin==1h start=="2025-01-01T00:00:00+10:00" stop=="2025-01-02T00:00:00+10:00"

# Daily data for one week
bin==1d start=="2025-01-01T00:00:00+10:00" stop=="2025-01-07T00:00:00+10:00"
```

## Migrating from v1

| v1 | v2 |
|---|---|
| `POST /api/v1/login/` with `email`, returns `{"key": ...}` | `POST /api/v2/token/` with `username` (form), returns `{"token": ...}` |
| `/api/v1/devices/`, `/api/v1/devices/{ref}/` | `/api/v2/sites/`, `/api/v2/sites/{id}/` |
| Device field `ref` | Site field `id` |
| `/api/v1/ts/series/`, `/api/v1/ts/table/` | `/api/v2/ts/series/`, `/api/v2/ts/table/` (same parameters) |
| `format=csv` | Removed; responses are JSON |
| `PHISAVER_URL`, `PHISAVER_USERNAME`, `PHISAVER_PASSWORD` | `PS_API_URL`, `PS_API_USERNAME`, `PS_API_PASSWORD` |
| `phisaver-client` 1.x | `phisaver-client` 2.x (`api.devices` → `api.sites`) |

New in v2: `/ts/heatmap/`, fleets, site metrics, switchboards, poles and IoTaWatts.

### Changes in 2.1

- New `/api/v2/sites/{site_id}/iotawatts/`: the IoTaWatts at one site. It returns 404 if you cannot see the site.
- `/api/v2/iotawatts/` accepts `site` (one id, or comma-separated ids).
- Every list endpoint accepts `id` (one id, or comma-separated ids).
- Switchboards include an `iotawatts` list (`id` and `name` of each IoTaWatt).
- `/api/v2/sites/{site_id}/metrics/` lists measured circuits only. Calculated metrics such as `Consumption` can still be queried.
- `phisaver-client` 2.1: `get_client()` and `get_client_from_env()` raise `errors.UnexpectedStatus` on any error response (e.g. 400, 404, 500), including from `sync_detailed()`. Pass `raise_on_unexpected_status=False` to get the previous behaviour. `get_client_from_env()` raises `RuntimeError` if a `PS_API_*` variable is missing.

## FAQ

### Where can I get support?
Contact PhiSaver support at [support@phisaver.com](mailto:support@phisaver.com).

### Can I use plain HTTP instead of HTTPS?

**No.** The PhiSaver API requires HTTPS for all requests. HTTP connections will be rejected. This ensures your credentials and energy data remain encrypted in transit.

### I'm getting a SSL certificate error. What should I do?
System-wide `httpie` may be using an outdated CA bundle. Try installing `httpie` in a Python virtual environment to get an up-to-date CA bundle. Alternatively, update your system's CA certificates. Alternatively, you can bypass SSL verification (not recommended for production) with the `--verify=no` flag in HTTPie.

### What's with the `==` syntax in HTTPie?
The use of "==" in HTTPie indicates query parameters, and "=" indicates form or JSON body fields. `:` indicates headers.

### Why do I get "was given 2 times"?
List parameters (`sites`, `mets`) must be a single comma-separated value, e.g. `mets=Production,Consumption`. If a parameter is repeated (`mets=Production&mets=Consumption`), the API returns 400.

## Requirements

- Python 3.9+
- Valid PhiSaver account credentials

## License

MIT
