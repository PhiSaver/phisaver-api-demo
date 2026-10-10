# Container settings
container_name := "phisaver-demo"
image_name := "localhost/phisaver-demo:latest"
runtime := "podman"

# PyPI index - set to "prod" to use main PyPI
pypi_env := env_var_or_default("PYPI_ENV", "test")
pypi_index := if pypi_env == "prod" { "https://pypi.org/simple/" } else { "https://test.pypi.org/simple/" }

workspace := justfile_directory()

# Show this help message
help:
    @echo "PhiSaver API Demo (dev only, not for general use)"
    @echo "Recipes:"
    @just --justfile {{justfile()}} --list --unsorted --list-heading ''
    @echo ""
    @echo "Examples:"
    @echo "  just build                  # Build with test.pypi.org"
    @echo "  just pypi_env=prod build    # Build with pypi.org"
    @echo "  just run                    # Run container interactively"

# Build the container image
build:
    @echo "Building container with {{pypi_env}} PyPI..."
    @{{runtime}} build \
        --build-arg PYPI_INDEX={{pypi_index}} \
        -t {{image_name}} \
        -f Containerfile \
        --quiet \
        . 2>&1 | tail -1
    @echo "Container built successfully"

# Run container interactively
run: build
    {{runtime}} run --replace -it \
        --name {{container_name}} \
        -v {{workspace}}:/workspace \
        {{image_name}}

# Remove container and image
clean:
    -{{runtime}} rm -f {{container_name}}
    -{{runtime}} rmi {{image_name}}
    @echo "Cleaned up container and image"

# Test HTTPie authentication
test-httpie: build
    @echo "Testing HTTPie authentication..."
    @{{runtime}} run --replace --name {{container_name}} -it \
        -v {{workspace}}:/workspace \
        {{image_name}} \
        bash -c 'set -a && source .env && set +a && http --ignore-stdin -f POST $PS_API_URL/api/v2/token/ username=$PS_API_USERNAME password=$PS_API_PASSWORD'

# Run all httpx examples
test-httpx: build
    @echo "Testing httpx example..."
    @{{runtime}} run --replace --name {{container_name}} -it \
        -v {{workspace}}:/workspace \
        {{image_name}} \
        bash -c 'set -a && source .env && set +a && for f in examples/httpx/0*.py; do echo "== $f"; python $f || exit 1; done'

# Run all phisaver-client examples
test-client: build
    @echo "Testing phisaver-client example..."
    @{{runtime}} run --replace --name {{container_name}} -it \
        -v {{workspace}}:/workspace \
        {{image_name}} \
        bash -c 'set -a && source .env && set +a && for f in examples/phisaver-client/0*.py; do echo "== $f"; python $f || exit 1; done'

# Run all tests
test-all: test-httpie test-httpx test-client

# Update OpenAPI schema file (dev only)
update-schema:
    cp ../phisaver/server/schema.yml .
    head -5 schema.yml
