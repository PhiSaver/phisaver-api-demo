# PhiSaver Client Library Examples

These examples demonstrate using the `phisaver-client` Python library - an auto-generated client with type hints and IDE autocomplete support.

## Prerequisites

See the [main README](../../README.md#authentication) for credentials and authentication details.

## Installation

Probably you want to use a virtual environment (venv, conda, etc.), but that's not required.

```bash
pip install phisaver-client 
```

## Usage

Set your credentials as environment variables (see [.env.example](../../.env.example)):

```bash
export PHISAVER_URL="https://app.phisaver.com"
export PHISAVER_USERNAME="demo@phisaver.com"
export PHISAVER_PASSWORD="checkthewebsiteoremailsupport"
```

Then run the examples:

```bash
python examples/phisaver-client/01_authenticate.py
python examples/phisaver-client/02_list_devices.py
python examples/phisaver-client/03_get_energy_data.py
```

## Examples

- [01_authenticate.py](01_authenticate.py) - Authenticate and get a client instance
- [02_list_devices.py](02_list_devices.py) - List devices and retrieve device details
- [03_get_energy_data.py](03_get_energy_data.py) - Fetch time-series energy data

## About This Client

The `phisaver-client` library is **automatically generated** from the PhiSaver API's [OpenAPI specification](../../schema.yml) using [openapi-python-client](https://github.com/openapi-generators/openapi-python-client).

## Other Languages

The OpenAPI specification can generate clients for many languages. The [OpenAPI Generator](https://openapi-generator.tech/) has a complete list of supported languages.
