# HTTPie Examples for PhiSaver API

[HTTPie](https://httpie.io/) is a user-friendly command-line HTTP client. These examples show how to interact with the PhiSaver API using HTTPie.

## Installation

```bash
# macOS
brew install httpie

# Linux
apt install httpie  # or: pip install httpie (see note re certificates below)

# Verify installation
http --version
```

## Setup

Set your credentials as environment variables:

```bash
export PS_API_URL="https://app.phisaver.com"
export PS_API_USERNAME="demo@phisaver.com"
export PS_API_PASSWORD="checkthewebsiteoremailsupport"
```

## 01. Authentication

Exchange your username and password for an API token (`-f` sends a form, as the token endpoint expects):

```bash
http -f POST $PS_API_URL/api/v2/token/ \
  username="$PS_API_USERNAME" \
  password="$PS_API_PASSWORD"
```

**Expected response:**
```json
{
    "token": "abc123def456..."
}
```

**Save the token:**
```bash
export TOKEN=$(http -f POST $PS_API_URL/api/v2/token/ \
  username="$PS_API_USERNAME" \
  password="$PS_API_PASSWORD" \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['token'])")

echo "Token: $TOKEN"
```

Send it on every request as `"Authorization:Token $TOKEN"`.

**Alternative: HTTPie Sessions (cookie-based):**

`/api/v2/login/` also starts a session, which HTTPie can store as cookies:

```bash
# Login with session - saves cookies automatically
http --session=phisaver POST $PS_API_URL/api/v2/login/ \
  email="$PS_API_USERNAME" \
  password="$PS_API_PASSWORD"

# Subsequent GET requests use saved cookies
http --session=phisaver GET $PS_API_URL/api/v2/sites/
```

Logging in again with an existing session returns `403 CSRF Failed`, because the saved cookie already authenticates you. Start a fresh session instead, e.g. `--session=phisaver2`, or delete the saved session under `~/.config/httpie/sessions/`.

## 02. Sites

List all sites your account can access:

```bash
http GET $PS_API_URL/api/v2/sites/ \
  "Authorization:Token $TOKEN"
```

Each site has an `id` (e.g. `demo1`) - use it in `sites==` for time-series queries.

**Filter sites** (comma-separated values are accepted):
```bash
http GET $PS_API_URL/api/v2/sites/ \
  "Authorization:Token $TOKEN" \
  name_prefix==Fac \
  data_status==Active,RecentlyInactive
```

Status values: `data_status` is one of `Active`, `RecentlyInactive`, `Inactive`, `NotStarted`, `Unknown`; `solar_status` is one of `Active`, `SubOptimal`, `Inactive`, `NotPresent`, `Unknown`.

**Get a specific site** (rates, location, metrics, switchboards, images):
```bash
http GET $PS_API_URL/api/v2/sites/demo1/ \
  "Authorization:Token $TOKEN"
```

## 03. Get Energy Data

This section demonstrates:
- Getting time-series data for specific metrics
- Using different binning intervals and time ranges
- Accessing data in table format for analysis
- Querying metrics by category
- Handling error responses

Replace `demo1`/`demo2` with site ids from your account, and pick dates where the site has data (see `last_data_at`).

### Example 1: Time-Series Data (Daily Bins)

```bash
http GET $PS_API_URL/api/v2/ts/series/ \
  "Authorization:Token $TOKEN" \
  sites==demo1 \
  start=="2025-01-01T00:00:00+10:00" \
  stop=="2025-01-07T00:00:00+10:00" \
  bin==1d \
  mets==Consumption,Production \
  units==W
```

### Example 2: Table Format (Multiple Sites)

Get one aggregated value per metric for multiple sites:

```bash
http GET $PS_API_URL/api/v2/ts/table/ \
  "Authorization:Token $TOKEN" \
  sites==demo1,demo2 \
  start=="2025-01-01T00:00:00+10:00" \
  stop=="2025-01-07T00:00:00+10:00" \
  units==kWh/day
```

### Example 3: Metrics by Category

Query all metrics in a category (e.g., all load circuits):

```bash
http GET $PS_API_URL/api/v2/ts/series/ \
  "Authorization:Token $TOKEN" \
  sites==demo1 \
  start=="2025-01-01T00:00:00+10:00" \
  stop=="2025-01-07T00:00:00+10:00" \
  bin==1d \
  metcat==load \
  units==kWh/day
```

### Example 4: Error Handling

Attempt an invalid query to see error response:

```bash
http GET $PS_API_URL/api/v2/ts/series/ \
  "Authorization:Token $TOKEN" \
  sites==demo1 \
  start=="2025-01-01T00:00:00+10:00" \
  stop=="2025-01-07T00:00:00+10:00" \
  bin==1h \
  metcat==InvalidMetric \
  units==W
```

This will return a 400 response showing which parameters are invalid.

## 04. Heatmap

`[day_of_year, hour, watts]` points (hourly averages), for time-of-day vs day plots. One site per request; units are always `W`:

```bash
http GET $PS_API_URL/api/v2/ts/heatmap/ \
  "Authorization:Token $TOKEN" \
  sites==demo1 \
  start=="2025-01-01T00:00:00+10:00" \
  stop=="2025-01-03T00:00:00+10:00" \
  mets==Net
```

## 05. Fleets

A fleet is a named group of sites.

```bash
# List fleets
http GET $PS_API_URL/api/v2/fleets/ "Authorization:Token $TOKEN"

# Fleet details, including its sites
http GET $PS_API_URL/api/v2/fleets/myfleet/ "Authorization:Token $TOKEN"

# Use fleet== in place of sites== in any time-series query
http GET $PS_API_URL/api/v2/ts/table/ \
  "Authorization:Token $TOKEN" \
  fleet==myfleet \
  duration==7d \
  units==kWh/day
```

## 06. Site Hardware: Metrics, Switchboards, Poles, IoTaWatts

```bash
# Metrics (circuits) at a site, with category - use these names in mets==
http GET $PS_API_URL/api/v2/sites/demo1/metrics/ "Authorization:Token $TOKEN"

# Switchboards at a site (each lists its IoTaWatts), then one switchboard's poles (circuit breakers)
http GET $PS_API_URL/api/v2/sites/demo1/switchboards/ "Authorization:Token $TOKEN"
http GET $PS_API_URL/api/v2/sites/demo1/switchboards/<switchboard_id>/poles/ "Authorization:Token $TOKEN"

# IoTaWatt energy monitors at a site
http GET $PS_API_URL/api/v2/sites/demo1/iotawatts/ "Authorization:Token $TOKEN"

# All IoTaWatts you can access (site== narrows to some sites), and one in detail (CTs, VT, phases)
http GET $PS_API_URL/api/v2/iotawatts/ "Authorization:Token $TOKEN"
http GET $PS_API_URL/api/v2/iotawatts/ "Authorization:Token $TOKEN" site==demo1,demo2
http GET $PS_API_URL/api/v2/iotawatts/<iotawatt_id>/ "Authorization:Token $TOKEN"
```

`/sites/demo1/metrics/` lists the site's measured circuits. Calculated metrics (`Consumption`, `Import`, `Export`, ...) are not listed, but you can still query them in `mets==`.

**Select items by id.** Every list accepts `id==` with one id or comma-separated ids:

```bash
http GET $PS_API_URL/api/v2/sites/demo1/metrics/ "Authorization:Token $TOKEN" id==Net,Production
http GET $PS_API_URL/api/v2/fleets/ "Authorization:Token $TOKEN" id==myfleet
```

## Tips

**Save response to file:**
```bash
http GET $PS_API_URL/api/v2/sites/ \
  "Authorization:Token $TOKEN" > sites.json
```

**Epoch timestamps** (easier for plotting/spreadsheets):
```bash
http GET $PS_API_URL/api/v2/ts/series/ \
  "Authorization:Token $TOKEN" \
  sites==demo1 \
  duration==7d \
  bin==1d \
  mets==Production \
  units==kWh/day \
  timeformat==epoch
```

**Verbose output (see request headers):**
```bash
http -v GET $PS_API_URL/api/v2/sites/ \
  "Authorization:Token $TOKEN"
```

## Query Parameters

Common parameters for `/ts/series/`, `/ts/table/` and `/ts/heatmap/`:

- `sites` - Comma-separated site ids (e.g., `demo1,demo2`), or `fleet` - a fleet id
- `start` - Start time (ISO8601 with timezone, or epoch seconds)
- `stop` - Stop time (default now)
- `duration` - Instead of `start`: length ending at `stop` (e.g. `7d`, `24h`)
- `bin` - Bin duration (`1h`, `30min`, `1d`, `1ME`) - `/ts/series/` only, required
- `mets` - Comma-separated metric names (`Production`, `Consumption`, `Net`), or `metcat` - a category
- `units` - Units (`W`, `kW`, `kWh/day`, `$/day`; heatmap is `W` only)
- `timeformat` - Output timestamps (`iso`, `epoch`, `epochms`)
- `timezone` - IANA timezone string (e.g., `Australia/Brisbane`)

See the [Cheat Sheet](../../CHEATSHEET.md) for all parameters.

## More Info

- [HTTPie Documentation](https://httpie.io/docs)
- [OpenAPI Schema](../../schema.yml)
