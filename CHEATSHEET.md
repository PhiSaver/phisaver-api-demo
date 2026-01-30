# PhiSaver API Cheat Sheet

Cheatsheet for PhiSaver API query parameters and usage patterns.

## Endpoints

### Time-Series Data
- **`/api/v1/ts/series/`** - Returns time-series data with timestamps
- **`/api/v1/ts/table/`** - Returns aggregated data without timestamps

### Device Management
- **`/api/v1/devices/`** - List all devices
- **`/api/v1/devices/{ref}/`** - Get specific device details

### Authentication
- **`/api/v1/login/`** - Authenticate and get API token

## Common Parameters

### Required Parameters

#### `start` (string)
Start time for the query (inclusive).

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

#### `stop` (string) OR `duration` (string)
End time for the query (exclusive) OR duration from start.

**Formats:**
- Same as `start` for `stop`
- Pandas timedelta for `duration`: `7d`, `24h`, `1W`, `1ME`

**Examples:**
```bash
stop="2025-01-07T00:00:00+10:00"     # ISO8601
duration=7d                           # 7 days from start
duration=24h                          # 24 hours from start
```

#### `bin` (string) - Only for `/ts/series/`
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
Comma-separated list of device identifiers.

**Examples:**
```bash
sites=demo1                    # Single device
sites=demo1,demo2              # Multiple devices
sites=demo1,demo2,demo3        # Three devices
```

### Metric Selection

#### `mets` (string)
Comma-separated list of metric/circuit names.

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
- `load` - All consumption circuits
- `production` - All solar/generation circuits
- `battery` - All battery circuits
- `net` - Grid import/export
- `calc` - Calculated metrics
- `other` - Other circuits

**Example:**
```bash
metcat=production              # All production metrics
metcat=load                    # All load/consumption metrics
```

### Units and Attributes

#### `units` (string)
Units of measurement. Valid values depend on endpoint and attribute.

**For `/ts/series/`: average value across the bin interval**
- `W` (recommended) - Watts
- `kW` - Kilowatts


**For `/ts/table/` (aggregated values):**
- `kWh/day` (recommended) - Kilowatt-hours per day
- `$/day` - Dollars per day

**Examples:**
```bash
# Time-series with kilowatts
/api/v1/ts/series/ ... units=kW

# Daily totals in kWh/day
/api/v1/ts/table/ ... units=kWh/day
```

#### `attribute` (string)
Physical attribute to query. Default is `power`. Other units not yet tested.

**Valid values:**
- `power` (default) - Power measurements
- `voltage` - Voltage measurements (beta)
- `current` - Current measurements (beta)
- `pf` - Power factor (beta)
- `soc` - State of charge (batteries) (beta)




### Output Format

#### `format` (string)
Response format.

**Valid values:**
- `json` (default) - JSON response
- `csv` - CSV download

**Example:**
```bash
format=json                    # JSON (default)
format=csv                     # CSV file
```

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

#### `function` (string)
Aggregation function for binning. Default is `mean`.

**Valid values:**
- `mean` (default) - Average value
- `sum` - Sum of values (beta)
- `max` - Maximum value (beta)

**Example:**
```bash
function=mean                  # Average (default)
function=sum                   # Sum values
```

### Data Source

#### `source` (string)
Data source to query. Default is `iotawatt`.

**Valid values:**
- `iotawatt` (default) - IoTaWatt energy monitor
- `inverter` - Solar inverter data (beta)
- `nem` - National Electricity Market data (beta)

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
Convert site references to human-readable names. Default is `false`.

**Example:**
```bash
named=true                     # Convert 'demo1' to 'Demo Device 01'
```

## More Information

- [HTTPie Examples](httpie/README.md) - Command-line examples
- [Python httpx Examples](httpx/) - Python HTTP client examples  
- [phisaver-client Examples](phisaver-client/) - Generated client library examples
- [OpenAPI Schema](../schema.yml) - Full API specification
