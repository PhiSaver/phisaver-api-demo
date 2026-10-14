# PyPI index - set PYPI_ENV=test to use test PyPI
pypi_env := env_var_or_default("PYPI_ENV", "prod")
pypi_index := if pypi_env == "prod" { "https://pypi.org/simple/" } else { "https://test.pypi.org/simple/" }

# The API version these examples are verified against (SSOT: VERSION.txt).
# Bump it by hand after re-verifying the examples against a new API (see `just check-api-version`).
api_version := `tr -d '[:space:]' < VERSION.txt`

# phisaver-client requirement: the client version follows the API, so pin to the verified version
# (~=2.1.5 means >=2.1.5,<2.2). Override with PS_CLIENT_REQ, e.g. PS_CLIENT_REQ=">=2.1" just install
client_req := env_var_or_default("PS_CLIENT_REQ", "~=" + api_version)

venv := justfile_directory() / ".venv"
bin := venv / "bin"

# Load PS_API_* settings from phisaver-api.env (direnv does the same via .envrc; CI sets them directly)
set dotenv-filename := "phisaver-api.env"
set dotenv-load

# Throttle: sleep this many ms before every API call (httpx via throttle/sitecustomize.py, HTTPie via `sleep`)
export THROTTLE_SLEEP_MS := env_var_or_default("THROTTLE_SLEEP_MS", "100")
export PYTHONPATH := justfile_directory() / "throttle"

# Show this help message
help:
    @echo "PhiSaver API Demo (API v{{api_version}}; dev only, not for general use)"
    @echo "Recipes:"
    @just --justfile {{justfile()}} --list --unsorted --list-heading ''
    @echo ""
    @echo "Examples:"
    @echo "  just install                # Create .venv and install packages"
    @echo "  PYPI_ENV=test just install  # Install from test.pypi.org"
    @echo "  just smoke                  # Quick check against the API"
    @echo "  just test-all               # Run all examples against the API"

# Create .venv and install packages
install:
    #!/usr/bin/env bash
    set -eu
    # Report on stderr: recipes depending on install capture stdout, e.g. token=$(just _access-token)
    exec >&2

    test -d {{venv}} || python3 -m venv {{venv}}
    echo "Installing phisaver-client{{client_req}} and httpx, httpie, ruff"
    {{bin}}/pip install --quiet --disable-pip-version-check \
        --index-url {{pypi_index}} --extra-index-url https://pypi.org/simple/ \
        "phisaver-client{{client_req}}" httpx httpie ruff
    if [ ! -f phisaver-api.env ]; then
        cp phisaver-api-example.env phisaver-api.env
        echo "Created phisaver-api.env from phisaver-api-example.env"
        echo "Edit it, to suit."
    fi
    echo "'just test-all' to verify the examples against the API"

[private]
_require-env:
    @test -n "${PS_API_USERNAME:-}" -a -n "${PS_API_PASSWORD:-}" || { echo "PS_API_USERNAME/PS_API_PASSWORD not set: create phisaver-api.env from phisaver-api-example.env"; exit 1; }

# Print a short-lived access token: sign in with email + password (JSON) at /api/v2/token/
[private]
_access-token: install _require-env
    #!/usr/bin/env bash
    set -eu
    sleep "$(awk -v ms="$THROTTLE_SLEEP_MS" 'BEGIN{print ms/1000}')"
    {{bin}}/http --ignore-stdin --check-status --body POST "${PS_API_URL%/}/api/v2/token/" \
        email="$PS_API_USERNAME" password="$PS_API_PASSWORD" \
        | {{bin}}/python -c 'import json, sys; print(json.load(sys.stdin)["access"])'

# Print the live API's version: info.version of its OpenAPI schema (JSON, read with the stdlib)
[private]
_api-version: install _require-env
    #!/usr/bin/env bash
    set -eu
    token=$(just --justfile {{justfile()}} _access-token)
    sleep "$(awk -v ms="$THROTTLE_SLEEP_MS" 'BEGIN{print ms/1000}')"
    {{bin}}/http --ignore-stdin --check-status --body --follow GET "${PS_API_URL%/}/api/v2/schema/" \
        format==json "Authorization:Bearer $token" \
        | {{bin}}/python -c 'import json, sys; print(json.load(sys.stdin)["info"]["version"].split()[0])'

# Remove .venv
clean:
    rm -rf {{venv}}
    @echo "Removed {{venv}}"

# Test HTTPie authentication (shows the access and refresh tokens)
test-httpie: install _require-env
    @sleep "$(awk -v ms="$THROTTLE_SLEEP_MS" 'BEGIN{print ms/1000}')"
    {{bin}}/http --ignore-stdin --check-status POST ${PS_API_URL%/}/api/v2/token/ email=$PS_API_USERNAME password=$PS_API_PASSWORD

# Run all httpx examples
test-httpx: install _require-env
    for f in examples/httpx/0*.py; do echo "== $f"; {{bin}}/python $f || exit 1; done

# Run all phisaver-client examples
test-client: install _require-env
    for f in examples/phisaver-client/0*.py; do echo "== $f"; {{bin}}/python $f || exit 1; done

# Run all tests
test-all: test-httpie test-httpx test-client

# Fail if the live API's version differs from the one these examples are verified against (VERSION.txt)
check-api-version: install _require-env
    #!/usr/bin/env bash
    set -eu
    live=$(just --justfile {{justfile()}} _api-version)
    if [ "$live" != "{{api_version}}" ]; then
        echo "Live API at $PS_API_URL is $live, but the examples are verified against {{api_version}} (VERSION.txt)."
        echo "Re-verify the examples against $live ('just test-all'), then set VERSION.txt to $live."
        exit 1
    fi
    echo "API version {{api_version}} OK ($PS_API_URL)"

# Download the OpenAPI schema (HTTPie only; needs credentials) and show its version
update-schema: install _require-env
    #!/usr/bin/env bash
    set -eu
    token=$(just --justfile {{justfile()}} _access-token)
    sleep "$(awk -v ms="$THROTTLE_SLEEP_MS" 'BEGIN{print ms/1000}')"
    {{bin}}/http --ignore-stdin --check-status --body --follow GET "${PS_API_URL%/}/api/v2/schema/" \
        "Authorization:Bearer $token" "Accept:application/vnd.oai.openapi" > schema.yml
    live=$(just --justfile {{justfile()}} _api-version)
    echo "schema.yml = API $live; examples are verified against {{api_version}} (VERSION.txt)"
    if [ "$live" != "{{api_version}}" ]; then
        echo "To move to $live: update the examples, 'just test-all', then set VERSION.txt to $live"
    fi

# Smoke test: authenticate, then the first example of each kind (fast, read-only)
smoke: install _require-env
    just --justfile {{justfile()}} _access-token > /dev/null
    {{bin}}/python examples/httpx/01_authenticate.py
    {{bin}}/python examples/phisaver-client/01_authenticate.py

# Lint and format-check the examples
lint: install
    {{bin}}/ruff check examples
    {{bin}}/ruff format --check examples
