# Multi-stage build for MCP GitLab Server
FROM python:3.14-slim as builder

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv for faster dependency management
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:${PATH}"

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv pip install --system --no-cache -e .

# Production stage
FROM python:3.14-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 mcpuser

# Set working directory
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=mcpuser:mcpuser . .

# Install the package
RUN pip install --no-deps -e .

# Switch to non-root user
USER mcpuser

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV GITLAB_URL=https://gitlab.com
ENV LOG_LEVEL=INFO

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import mcp_gitlab; print('healthy')" || exit 1

# Default command
CMD ["python", "-m", "mcp_gitlab"]

# Labels
LABEL org.opencontainers.image.source="https://github.com/Vijay-Duke/mcp-gitlab"
LABEL org.opencontainers.image.description="MCP server for GitLab integration"
LABEL org.opencontainers.image.licenses="Apache-2.0"