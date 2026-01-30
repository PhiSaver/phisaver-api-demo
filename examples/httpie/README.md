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
export PHISAVER_URL="https://app.phisaver.com"
export PHISAVER_USERNAME="demo@phisaver.com"
export PHISAVER_PASSWORD="checkthewebsiteoremailsupport"
```

## 01. Authentication

Authenticate and get an API token:

```bash
http POST $PHISAVER_URL/api/v1/login/ \
  email="$PHISAVER_USERNAME" \
  password="$PHISAVER_PASSWORD"
```

**Expected response:**
```json
{
    "key": "abc123def456..."
}
```

**Save the token:**
```bash
export TOKEN=$(http POST $PHISAVER_URL/api/v1/login/ \
  email="$PHISAVER_USERNAME" \
  password="$PHISAVER_PASSWORD" \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['key'])")

echo "Token: $TOKEN"
```

**Alternative: HTTPie Sessions (cookie-based):**

HTTPie sessions use cookies instead of tokens:

```bash
# Login with session - saves cookies automatically
http --session=phisaver POST $PHISAVER_URL/api/v1/login/ \
  email="$PHISAVER_USERNAME" \
  password="$PHISAVER_PASSWORD"

# Subsequent requests use saved cookies
http --session=phisaver GET $PHISAVER_URL/api/v1/devices/
```

## 02. List Devices

Get all devices:

```bash
http GET $PHISAVER_URL/api/v1/devices/ \
  "Authorization:Token $TOKEN"
```

**Get a specific device:**
```bash
http GET $PHISAVER_URL/api/v1/devices/demo1/ \
  "Authorization:Token $TOKEN"
```

## 03. Get Energy Data

This section demonstrates:
- Getting time-series data for specific metrics
- Using different binning intervals and time ranges
- Accessing data in table format for analysis
- Querying metrics by category
- Handling error responses

### Example 1: Time-Series Data (Daily Bins)

```bash
http GET $PHISAVER_URL/api/v1/ts/series/ \
  "Authorization:Token $TOKEN" \
  sites==demo1 \
  start=="2025-01-01T00:00:00+10:00" \
  stop=="2025-01-07T00:00:00+10:00" \
  bin==1d \
  mets==Consumption,Production \
  units==W
```

### Example 2: Table Format (Multiple Sites)

Get aggregated data for multiple devices:

```bash
http GET $PHISAVER_URL/api/v1/ts/table/ \
  "Authorization:Token $TOKEN" \
  sites==demo1,demo2 \
  start=="2025-01-01T00:00:00+10:00" \
  stop=="2025-01-07T00:00:00+10:00" \
  units==kWh/day
```

### Example 3: Metrics by Category

Query all metrics in a category (e.g., all load circuits):

```bash
http GET $PHISAVER_URL/api/v1/ts/series/ \
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
http GET $PHISAVER_URL/api/v1/ts/series/ \
  "Authorization:Token $TOKEN" \
  sites==demo1 \
  start=="2025-01-01T00:00:00+10:00" \
  stop=="2025-01-07T00:00:00+10:00" \
  bin==1h \
  metcat==InvalidMetric \
  units==W
```

This will return an error response showing which parameters are invalid.

## Tips

**Save response to file:**
```bash
http GET $PHISAVER_URL/api/v1/devices/ \
  "Authorization:Token $TOKEN" > devices.json
```

**Download as CSV:**
```bash
http GET $PHISAVER_URL/api/v1/ts/series/ \
  "Authorization:Token $TOKEN" \
  sites==demo1 \
  start=="2025-01-01T00:00:00+10:00" \
  stop=="2025-01-07T00:00:00+10:00" \
  bin==1d \
  mets==Production \
  units==kWh/day \
  format==csv > data.csv
```

**Verbose output (see request headers):**
```bash
http -v GET $PHISAVER_URL/api/v1/devices/ \
  "Authorization:Token $TOKEN"
```

## Query Parameters

Common parameters for `/ts/series/` endpoint:

- `sites` - Comma-separated site identifiers (e.g., `demo1,demo2`)
- `start` - Start time (ISO8601 format with timezone)
- `stop` - Stop time (ISO8601 format with timezone)
- `bin` - Bin duration (`1h`, `30min`, `1d`, `1M`)
- `mets` - Comma-separated metric names (`Production`, `Consumption`, `Export`)
- `units` - Units of measurement (`W`, `kW`, `kWh`, `kWh/day`, `$/day`)
- `format` - Response format (`json`, `csv`)
- `timezone` - IANA timezone string (e.g., `Australia/Brisbane`)

## More Info

- [HTTPie Documentation](https://httpie.io/docs)
- [PhiSaver API Documentation](https://phisaver.com/docs)
