FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Set work directory
WORKDIR /app

# Install system dependencies and uv
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy Python project files
COPY pyproject.toml ./

# Create virtual environment and install dependencies with uv
RUN uv venv /opt/venv --python 3.11
ENV PATH="/opt/venv/bin:$PATH"

# Install project dependencies (production + dev for testing)
RUN uv pip install --no-cache -e .

# Copy project
COPY . .

# Create uploads directory
RUN mkdir -p /app/uploads

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]