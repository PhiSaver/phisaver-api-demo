# Phisaver API Usage

This folder contains sample code and documentation for using the PhiSaver API.

PhiSaver provides secure access to private energy data for residential and commercial solar installations. This document shows developers and researchers how to retrieve device information and time-series energy data.

The API is described by a [schema](schema.yml) using the OpenAPI v3 specification.

*Three* methods are documented to interact with the API:
1. Command-line HTTP 
2. Direct HTTP requests using Python 
3. Python client library using [phisaver-client](https://pypi.org/project/phisaver-client/)

For advanced users, OpenAPI clients can be auto-generated for other languages. The phisaver-client, above, is the reference example. 

## Authentication

The API requires authentication for all requests. 

Existing users can use their email and password to access their data. 

The demo account has an *unchanging* token for convenience. Production accounts will have rotating tokens.

**Demo Credentials**:
- **URL**: `https://app.phisaver.com`
- **Username**: `demo@phisaver.com`
- **Password**: `checkthewebsiteoremailsupport`


## Quick Start

The quickest way to explore the API is using [HTTPie](https://httpie.io/), a user-friendly command-line HTTP client. You could also use `curl` or `wget`. 

```bash
# Install HTTPie
apt install httpie  # Linux (use brew or python pip on other OSes)

# Set credentials as environment variables
export PHISAVER_URL="https://app.phisaver.com"
export PHISAVER_USERNAME="your_email@example.com"
export PHISAVER_PASSWORD="your_password"

# Authenticate and save token
export TOKEN=$(http POST $PHISAVER_URL/api/v1/login/ \
  email="$PHISAVER_USERNAME" \
  password="$PHISAVER_PASSWORD" \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['key'])")

# Get time-series energy data
http GET $PHISAVER_URL/api/v1/ts/series/ \
  "Authorization:Token $TOKEN" \
  sites==demo1 \
  start=="2025-01-01T00:00:00+10:00" \
  stop=="2025-01-07T00:00:00+10:00" \
  bin==1d \
  mets==Production \
  units==kWh
```

## Three Ways to Interact with the PhiSaver API

### 1. HTTPie (Command Line)

**Best for**: Quick exploration, debugging, shell scripts, learning the API

HTTPie is a simple, intuitive command-line HTTP client with JSON, sessions and colorized output. 

**Installation:**
```bash
brew install httpie  # macOS
apt install httpie   # Linux
pip install httpie   # Python
```

**[HTTPie README](examples/httpie/README.md)** 
**[HTTPie examples](examples/httpie/)** 

---

### 2. Python + httpx

**Best for**: Production applications, async/await support, HTTP/2, custom integrations

Direct HTTP requests using the modern `httpx` library without the generated client wrapper.

**Installation:**
```bash
pip install httpx
```

**[httpx examples](examples/httpx/)** - Complete Python scripts using httpx

---

### 3. Python + phisaver-client

**Best for**: Type-safe Python applications, IDE autocomplete, generated from OpenAPI spec

Auto-generated Python client library with type hints and full API coverage.

**Installation:**
```bash
pip install phisaver-client --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/
```

**[phisaver-client README](examples/phisaver-client/README.md)**
**[phisaver-client examples](examples/)** - Complete Python scripts using phisaver-client

## API Details

### Time Ranges

**Input formats:**
- **ISO8601** (recommended): `2025-01-01T00:00:00+10:00` - includes timezone
- **Epoch seconds**: `1735668000` - Unix timestamp
- **Duration**: Use `duration` parameter instead of `stop` (e.g., `duration=7d`)

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

# Output as epoch milliseconds
timeformat==epochms
```

### Devices (Sites)

Query single or multiple devices using the `sites` parameter:

**Single device:**
```bash
sites==demo1
```

**Multiple devices:**
```bash
sites==demo1,demo2,demo3
```

**Fleet (predefined groups):**
```bash
fleet==myfleet  # Equivalent to sites==site1,site2,site3
```

### Metrics and Circuits

**Select metrics** using `mets` parameter:
```bash
# Single metric
mets==Production

# Multiple metrics
mets==Production,Consumption,FeedIn
```

**Filter by category** using `metcat` parameter:
- `load` - Consumption circuits
- `production` - Solar/generation circuits
- `battery` - Battery circuits
- `net` - Grid import/export
- `calc` - Calculated metrics
- `other` - Other circuits

**Example:**
```bash
# Get all production circuits
metcat==production

# Get specific circuits by name
mets==Production,AirConditioner,HotWater
```

### Units

Units differ between `/ts/series/` and `/ts/table/` endpoints:

**For /ts/series/ (time-series data):**
- `W` (default) - Instantaneous power in watts
- `kW` - Instantaneous power in kilowatts

**For /ts/table/ (aggregated data):**
- `kWh/day` (recommended) - Energy per day
- `$/day` - Cost per day

**Example:**
```bash
# Time-series with instantaneous power
/api/v1/ts/series/ ... units==kW

# Table with daily energy
/api/v1/ts/table/ ... units==kWh/day
```

### Binning

Group data into time intervals using the `bin` parameter (only for `/ts/series/`):

**Common bins:**
- `1h` - Hourly
- `30min` - Half-hourly
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

### Complete Example

```bash
# Get daily production and consumption for multiple devices
http GET $PHISAVER_URL/api/v1/ts/series/ \
  "Authorization:Token $TOKEN" \
  sites==demo1,demo2 \
  start=="2025-01-01T00:00:00+10:00" \
  stop=="2025-01-31T00:00:00+10:00" \
  bin==1d \
  mets==Production,Consumption \
  units==kW \
  timeformat==iso \
  format==json
```

See [examples/API_REFERENCE.md](examples/API_REFERENCE.md) for detailed parameter documentation.

## FAQ

### Where can I get support?
Contact PhiSaver support at [support@phisaver.com](mailto:support@phisaver.com).

### Can I use plain HTTP instead of HTTPS?

**No.** The PhiSaver API requires HTTPS for all requests. HTTP connections will be rejected. This ensures your credentials and energy data remain encrypted in transit.

### I'm getting a SSL certificate error. What should I do?
System-wide `httpie` may be using an outdated CA bundle. Try installing `httpie` in a Python virtual environment to get an up-to-date CA bundle. Alternatively, update your system's CA certificates. Alternatively, you can bypass SSL verification (not recommended for production) with the `--verify=no` flag in HTTPie:

### What's with the `==` syntax in HTTPie?
The use of "==" in HTTPie indicates query parameters, and "=" indicates headers or JSON body fields.

## Requirements

- Python 3.9+
- Valid PhiSaver account credentials

## License

MIT
