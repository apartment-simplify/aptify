# Use a slim Python image
FROM python:3.10.14-slim

# Set working directory
WORKDIR /app

# Copy pyproject.toml and lockfile first (for caching)
COPY pyproject.toml uv.lock README.md ./
COPY documents /app/documents

# Install pip and build tools
RUN pip install --upgrade pip setuptools wheel hatch

# Install dependencies using Hatch
RUN uv sync

# Copy the source code
COPY src/ ./src/

# Expose FastAPI port
EXPOSE 8000

# Start API with uv
CMD ["uv", "run", "uvicorn", "src.aptify_api.app:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
