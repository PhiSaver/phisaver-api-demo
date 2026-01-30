# Makefile for PhiSaver API Demo Container
# Not intended for typical end users; for development and testing purposes.

# Container settings
CONTAINER_NAME = phisaver-demo
IMAGE_NAME = localhost/phisaver-demo:latest
RUNTIME = podman

# PyPI index - set to "production" to use main PyPI
PYPI_ENV ?= test
ifeq ($(PYPI_ENV),production)
	PYPI_INDEX = https://pypi.org/simple/
else
	PYPI_INDEX = https://test.pypi.org/simple/
endif

.PHONY: help build run shell clean

help:  ## Show this help message
	@echo "PhiSaver API Demo - Container Management"
	@echo ""
	@echo "Usage: make [target] [PYPI_ENV=test|production]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'
	@echo ""
	@echo "Examples:"
	@echo "  make build              # Build with test.pypi.org"
	@echo "  make build PYPI_ENV=production  # Build with pypi.org"
	@echo "  make run                # Run container interactively"
	@echo "  make shell              # Start bash shell in container"

build:  ## Build the container image
	@echo "Building container with $(PYPI_ENV) PyPI ($(PYPI_INDEX))..."
	$(RUNTIME) build \
		--build-arg PYPI_INDEX=$(PYPI_INDEX) \
		-t $(IMAGE_NAME) \
		-f Containerfile \
		.
	@echo "Container built successfully"
	@echo "Run 'make shell' to start the container"

run: build  ## Run container interactively
	$(RUNTIME) run --replace -it \
		--name $(CONTAINER_NAME) \
		-v $(PWD):/workspace \
		$(IMAGE_NAME)


clean:  ## Remove container and image
	-$(RUNTIME) rm -f $(CONTAINER_NAME)
	-$(RUNTIME) rmi $(IMAGE_NAME)
	@echo "Cleaned up container and image"

test-httpie: build  ## Test HTTPie authentication
	@echo "Testing HTTPie authentication..."
	$(RUNTIME) run --replace --name $(CONTAINER_NAME) -it \
		-v $(PWD):/workspace \
		$(IMAGE_NAME) \
		bash -c 'set -a && source .env && set +a && http --ignore-stdin POST $$PHISAVER_URL/api/v1/login/ email=$$PHISAVER_USERNAME password=$$PHISAVER_PASSWORD'

test-httpx: build  ## Test httpx example
	@echo "Testing httpx example..."
	$(RUNTIME) run --replace --name $(CONTAINER_NAME) -it \
		-v $(PWD):/workspace \
		$(IMAGE_NAME) \
		bash -c 'set -a && source .env && set +a && python examples/httpx/03_get_energy_data.py'

test-client: build  ## Test phisaver-client example
	@echo "Testing phisaver-client example..."
	$(RUNTIME) run --replace --name $(CONTAINER_NAME) -it \
		-v $(PWD):/workspace \
		$(IMAGE_NAME) \
		bash -c 'set -a && source .env && set +a && python examples/phisaver-client/03_get_energy_data.py'

test-all: test-httpie test-httpx test-client  ## Run all tests

.DEFAULT_GOAL := help
