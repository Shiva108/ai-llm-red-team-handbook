# Prompt Injection Tester (PIT) - Docker Image
# Version: 2.0.0
# Architecture: Sequential 4-Phase Pipeline

FROM python:3.11-slim

# Metadata
LABEL maintainer="AI LLM Red Team Handbook"
LABEL version="2.0.0"
LABEL description="Prompt Injection Testing tool with sequential pipeline architecture"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    curl \
    ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml README.md ./
COPY pit/ ./pit/
COPY tests/ ./tests/

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Create directory for reports
RUN mkdir -p /reports

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PIT_OUTPUT_DIR=/reports

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD pit --version || exit 1

# Default command (show help)
ENTRYPOINT ["pit"]
CMD ["--help"]

# Usage examples:
# Build: docker build -t pit:2.0.0 .
# Run: docker run -v $(pwd)/reports:/reports pit:2.0.0 scan http://host.docker.internal:11434/api/chat --auto
# Interactive: docker run -it pit:2.0.0 scan http://target-url --auto
