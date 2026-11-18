# Use official Python slim image (3.12 is more stable for these packages)
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install runtime dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app

# Expose the port Cloud Run expects
ENV PORT=8080

# Create non-root user
RUN adduser --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# Expose port for clarity
EXPOSE 8080

# Start Gunicorn with Uvicorn worker
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "main:app", "--bind", "0.0.0.0:8080", "--threads", "1"]