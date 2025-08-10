# Multi-stage build for Crystal Bay Travel System
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY pyproject.toml uv.lock ./
RUN pip install --upgrade pip
RUN pip install uv
RUN uv sync --frozen

# Production stage
FROM python:3.11-slim

# Labels for container metadata
LABEL maintainer="Crystal Bay Travel <tech@crystalbay.travel>"
LABEL description="Crystal Bay Travel - Multi-Channel Travel Booking System"
LABEL version="1.0.0"

# Set working directory
WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    libpq-dev \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy virtual environment from builder stage
COPY --from=builder /app/.venv /app/.venv

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production

# Copy application code
COPY . .

# Create required directories with proper permissions
RUN mkdir -p data logs static/uploads templates \
    && chown -R appuser:appuser /app

# Clean up development files and unnecessary content
RUN rm -rf \
    attached_assets \
    backup \
    tests \
    __pycache__ \
    *.log \
    .replit* \
    replit.nix \
    replit_agent \
    .git \
    .gitignore \
    comprehensive_system_analysis_report.md \
    priority_fixes_plan.md \
    tinyproxy_setup.md \
    vps_script_solution.md \
    vps_setup_guide.md \
    *.md.backup \
    temp \
    .tmp

# Switch to non-root user
USER appuser

# Add health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Expose port
EXPOSE 5000

# Start command with production settings
CMD ["gunicorn", \
     "--bind", "0.0.0.0:5000", \
     "--workers", "2", \
     "--worker-class", "sync", \
     "--timeout", "120", \
     "--max-requests", "1000", \
     "--max-requests-jitter", "50", \
     "--preload", \
     "--log-level", "info", \
     "main:app"]