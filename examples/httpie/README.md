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

**Save the token for later use:**
```bash
export TOKEN=$(http POST $PHISAVER_URL/api/v1/login/ \
  email="$PHISAVER_USERNAME" \
  password="$PHISAVER_PASSWORD" | jq -r '.key')

echo "Token: $TOKEN"
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

**Pretty print with jq:**
```bash
http GET $PHISAVER_URL/api/v1/devices/ \
  "Authorization:Token $TOKEN" | jq '.[] | {name, ref, solar, timezone}'
```

## 03. Get Energy Data

**Get time-series data (daily bins):**

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

**Get hourly data:**

```bash
http GET $PHISAVER_URL/api/v1/ts/series/ \
  "Authorization:Token $TOKEN" \
  sites==demo1 \
  start=="2025-01-01T00:00:00+10:00" \
  stop=="2025-01-02T00:00:00+10:00" \
  bin==1h \
  mets==Production \
  units==kWh/day
```

**Get table format data:**

```bash
http GET $PHISAVER_URL/api/v1/ts/table/ \
  "Authorization:Token $TOKEN" \
  sites==demo1 \
  start=="2025-01-01T00:00:00+10:00" \
  stop=="2025-01-07T00:00:00+10:00" \
  units==kWh/day
```

**Multiple sites:**

```bash
http GET $PHISAVER_URL/api/v1/ts/series/ \
  "Authorization:Token $TOKEN" \
  sites==demo1,demo2 \
  start=="2025-01-01T00:00:00+10:00" \
  stop=="2025-01-07T00:00:00+10:00" \
  bin==1d \
  mets==Production \
  units==kWh/day
```

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

**Use sessions (auto-saves token):**
```bash
# Create session
http --session=phisaver POST $PHISAVER_URL/api/v1/auth/token/login/ \
  username="$PHISAVER_USERNAME" \
  password="$PHISAVER_PASSWORD"

# Subsequent requests use the session
http --session=phisaver GET $PHISAVER_URL/api/v1/devices/
```

## Query Parameters

Common parameters for `/ts/series/` endpoint:

- `sites` - Comma-separated site identifiers (e.g., `demo1,demo2`)
- `start` - Start time (ISO8601 format with timezone)
- `stop` - Stop time (ISO8601 format with timezone)
- `bin` - Bin duration (`1h`, `30min`, `1d`, `1M`)
- `mets` - Comma-separated metric names (`Production`, `Consumption`, `FeedIn`)
- `units` - Units of measurement (`W`, `kW`, `kWh`, `kWh/day`, `$/day`)
- `format` - Response format (`json`, `csv`)
- `timezone` - IANA timezone string (e.g., `Australia/Brisbane`)

## More Info

- [HTTPie Documentation](https://httpie.io/docs)
- [PhiSaver API Documentation](https://phisaver.com/docs)
