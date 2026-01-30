# Containerfile for PhiSaver API Demo
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Copy environment template and examples
COPY .env.example .env.example
COPY .env.example .env
COPY examples/ examples/
COPY schema.yml schema.yml
COPY README.md README.md

# Install Python packages
ARG PYPI_INDEX=https://test.pypi.org/simple/
RUN pip install --no-cache-dir \
    --disable-pip-version-check \
    --root-user-action=ignore \
    --quiet \
    --index-url ${PYPI_INDEX} \
    --extra-index-url https://pypi.org/simple/ \
    phisaver-client httpx httpie

# Auto-source .env on shell startup
RUN echo 'set -a && source /workspace/.env && set +a' >> /root/.bashrc

# Default command
CMD ["/bin/bash"]
