# Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (including Tesseract OCR for scanned PDF support)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    tesseract-ocr \
    tesseract-ocr-eng \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Install Playwright dependencies
RUN pip install playwright && playwright install-deps && playwright install chromium

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8080

# Default command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
