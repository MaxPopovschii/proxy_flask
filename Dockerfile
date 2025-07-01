FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies and clean up in the same layer
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (better layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy only necessary files
COPY proxy.py .
COPY config.yaml .

# Create non-root user for security
RUN useradd -m appuser \
    && chown -R appuser:appuser /app
USER appuser

# Expose the application port
EXPOSE 10000

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    LISTEN_HOST=0.0.0.0 \
    LISTEN_PORT=10000 \
    REQUEST_TIMEOUT=10

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
    CMD curl -f http://localhost:10000/health || exit 1

# Run the application
CMD ["python", "proxy.py"]
