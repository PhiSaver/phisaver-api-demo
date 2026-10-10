# PhiSaver API Cheat Sheet

Cheatsheet for PhiSaver API (v2) query parameters and usage patterns.

## Endpoints

### Authentication

- **`POST /api/v2/token/`** - Exchange `username` and `password` (form-encoded) for `{"token": ...}`. Send `Authorization: Token <token>` on every request.
- **`POST /api/v2/login/`** - Session login (`email` + `password`), e.g. for HTTPie sessions

### Time-Series Data

- **`/api/v2/ts/series/`** - Returns time-series data with timestamps: `{site: {metric: [[timestamp, value], ...]}}`
- **`/api/v2/ts/table/`** - Returns aggregated data without timestamps: `{site: {metric: value}}`
- **`/api/v2/ts/heatmap/`** - Returns hourly heatmap points for ONE site: `{site: {metric: [[day_of_year, hour, watts], ...]}}`. Days are 1-365 on a non-leap calendar (Feb 29 is dropped), so the same date lines up across years. No `fleet` or `bin`.

### Sites

- **`/api/v2/sites/`** - List all sites you can access
- **`/api/v2/sites/{id}/`** - Get specific site details
- **`/api/v2/sites/{site_id}/metrics/`** - Measured circuits at a site (calculated metrics such as `Consumption` are not listed)
- **`/api/v2/sites/{site_id}/metrics/{id}/`** - One metric
- **`/api/v2/sites/{site_id}/switchboards/`** - Switchboards at a site, each with its IoTaWatts
- **`/api/v2/sites/{site_id}/switchboards/{id}/`** - One switchboard, with its IoTaWatts and poles
- **`/api/v2/sites/{site_id}/switchboards/{switchboard_id}/poles/`** - Poles (circuit breakers) in a switchboard
- **`/api/v2/sites/{site_id}/iotawatts/`** - IoTaWatts at a site (404 if you cannot see the site)

### Fleets

- **`/api/v2/fleets/`** - List fleets (named groups of sites)
- **`/api/v2/fleets/{id}/`** - Fleet details, including its sites

### IoTaWatts

- **`/api/v2/iotawatts/`** - List IoTaWatt energy monitors. `site=demo1,demo2` limits the list to those sites
- **`/api/v2/iotawatts/{id}/`** - IoTaWatt details: CTs, voltage reference, phases

## List Filters

Every list endpoint (sites, fleets, IoTaWatts, metrics, switchboards, poles) accepts `id`: one id or comma-separated ids, e.g. `id=demo1,demo2`.

`/api/v2/iotawatts/` also accepts `site`: one site id or comma-separated site ids.

`/api/v2/sites/` also accepts the filters below. Each takes a single value or comma-separated values.

- `name_prefix` - Case-insensitive site name prefix
- `data_status` - `Active`, `RecentlyInactive`, `Inactive`, `NotStarted`, `Unknown`
- `solar_status` - `Active`, `SubOptimal`, `Inactive`, `NotPresent`, `Unknown`

## Common Time-Series Parameters

**List parameters (`sites`, `mets`) take ONE comma-separated value.** A repeated parameter (`mets=A&mets=B`) is rejected with 400.

### Required Parameters

#### `start` (string) - or `duration`

Start time for the query (inclusive). Give any two of `start`, `stop` and `duration`; `stop` alone defaults to now, so `start` or `duration` is required.

**Formats:**

- ISO8601 with timezone: `2025-01-01T00:00:00+10:00`
- ISO8601 UTC: `2025-01-01T00:00:00Z`
- Epoch seconds: `1735668000`

**Examples:**

```bash
start="2025-01-01T00:00:00+10:00"    # ISO8601 with AEST
start="2025-01-01T00:00:00Z"          # ISO8601 UTC
start=1735668000                      # Epoch seconds
```

#### `stop` (string)

End time for the query (exclusive). Defaults to now. Same formats as `start`.

```bash
stop="2025-01-07T00:00:00+10:00"     # ISO8601
```

#### `duration` (string)

Length of the query. With `start`, the window begins at `start`; otherwise it ends at `stop` (or now). Do not give all three of `start`, `stop` and `duration`.

**Formats:** pandas offset, ISO 8601 duration or plain seconds: `7d`, `24h`, `P1D`, `3600`

**Examples:**

```bash
duration=7d                                       # last 7 days
duration=24h stop="2025-01-07T00:00:00+10:00"     # 24 hours before stop
duration=7d start="2025-01-01T00:00:00+10:00"     # 7 days from start
```

#### `bin` (string) - Required for `/ts/series/` only

Not used by `/ts/table/`. Rejected by `/ts/heatmap/`, which is always hourly.

Time interval for grouping data points.

**Valid values:**

- `1min`, `5min`, `15min`, `30min` - Minutes
- `1h`, `2h`, `6h`, `12h` - Hours  
- `1d` - Daily
- `1W` - Weekly
- `1ME` - Month-end
- Any pandas DateOffset string

**Examples:**

```bash
bin=1h      # Hourly bins
bin=30min   # 30-minute bins
bin=1d      # Daily bins
bin=1ME     # Monthly bins (month-end)
```

### Site Selection

#### `sites` (string)

Comma-separated list of site ids (the `id` field from `/api/v2/sites/`).

**Examples:**

```bash
sites=demo1                    # Single site
sites=demo1,demo2              # Multiple sites
sites=demo1,demo2,demo3        # Three sites
```

#### `fleet` (string)

A fleet id, used instead of `sites`. Equivalent to listing every site in the fleet. Not supported by `/ts/heatmap/` (one site only).

```bash
fleet=myfleet
```

### Metric Selection

#### `mets` (string)

Comma-separated list of metric/circuit names. A site's metrics are listed at `/api/v2/sites/{id}/metrics/`.

**Common metrics:**

- `Production` - Solar production
- `Consumption` - Total consumption
- `Import` - Import from grid (unsigned)
- `Export` - Export to grid (unsigned)
- `Net` - Net grid flow (signed positive for import, negative for export)
- Circuit names: `AirConditioner`, `HotWater`, `Pool`, etc.

**Examples:**

```bash
mets=Production                        # Single metric
mets=Production,Consumption            # Two metrics
mets=Production,Consumption,Export     # Three metrics
```

#### `metcat` (string)

Filter metrics by category instead of naming them explicitly.

**Valid values:**

- `load` - All consumption circuits (every metric not listed below)
- `production` - Solar: `Production`
- `battery` - `Battery`, `BatteryCharge`, `BatteryDischarge`
- `net` - Grid: `Net`, `Import`, `Export`
- `calc` - Calculated: `Consumption`, `FreeConsumption`, `ImportConsumption`, `Unmonitored`
- `other` - Reserved; no metric currently has this category
- `all` - Every metric

Each metric belongs to exactly one category.

**Example:**

```bash
metcat=net                     # Net, Import, Export
metcat=load                    # All load/consumption metrics
```

### Units and Attributes

#### `units` (string)

Units of measurement, for `attribute=power` only. Valid values: `W`, `kW`, `kWh/day`, `$/day`. Heatmap accepts `W` only.

**For `/ts/series/`: average value across the bin interval**

- `W` (recommended) - Watts
- `kW` - Kilowatts


**For `/ts/table/` (aggregated values):**

- `kWh/day` (recommended) - Kilowatt-hours per day
- `$/day` - Dollars per day

**Examples:**

```bash
# Time-series with kilowatts
/api/v2/ts/series/ ... units=kW

# Daily totals in kWh/day
/api/v2/ts/table/ ... units=kWh/day
```

#### `attribute` (string)

Physical attribute to query. Default is `power`.

| Endpoint | Valid values |
| --- | --- |
| `/ts/series/` | `power` (default), `soc` |
| `/ts/table/` | `power` |
| `/ts/heatmap/` | `power` |

- `power` - Power measurements (see `units`)
- `soc` - Battery state of charge, as a fraction from 0 to 1. Use with `mets=Battery`, `source=inverter` and `engine=timescale` (inverter data is stored in TimescaleDB). `units` does not apply.

**Example:**

```bash
/api/v2/ts/series/ ... mets=Battery attribute=soc source=inverter engine=timescale
```

### Output Format

Responses are JSON. (v1's `format=csv` is not available in v2.)

#### `timeformat` (string)

Timestamp format in response.

**Valid values:**

- `iso` (default) - ISO8601 strings
- `epoch` - Unix timestamp (seconds)
- `epochms` - Unix timestamp (milliseconds)

**Examples:**

```bash
timeformat=iso                 # "2025-01-01T00:00:00+10:00"
timeformat=epoch               # 1735668000
timeformat=epochms             # 1735668000000
```

### Timezone

#### `timezone` (string)

IANA timezone string for the query. Defaults to the first site's timezone.

**Common timezones:**

- `Australia/Brisbane` - AEST (no DST)
- `Australia/Sydney` - AEST/AEDT (with DST)
- `Australia/Perth` - AWST
- `UTC` - Coordinated Universal Time

**Example:**

```bash
timezone=Australia/Brisbane
timezone=UTC
```

### Aggregation

#### `function` (string) - `/ts/series/` and `/ts/table/`

Aggregation function for binning. Only `mean` (the default) is currently accepted.

### Data Source

#### `source` (string)

Data source to query. Default is `iotawatt`.

**Valid values:**

- `iotawatt` (default) - IoTaWatt energy monitor
- `inverter` - Solar inverter data (beta)
- `nem` - National Electricity Market data (beta)
- `calc` - Calculated data (beta)

**Example:**

```bash
source=iotawatt                # IoTaWatt (default)
source=inverter                # Inverter data
```

#### `engine` (string)

Database engine to use. Default is `influx`.

**Valid values:**

- `influx` (default) - InfluxDB
- `timescale` - TimescaleDB (beta)


### Other Options

#### `named` (boolean)

Convert site ids to human-readable names in the response. Default is `false`.

**Example:**

```bash
named=true                     # Convert 'demo1' to 'Demo Device 01'
```

## More Information

- [HTTPie Examples](examples/httpie/README.md) - Command-line examples
- [Python httpx Examples](examples/httpx/) - Python HTTP client examples  
- [phisaver-client Examples](examples/phisaver-client/) - Generated client library examples
- [OpenAPI Schema](schema.yml) - Full API specification
