FROM python:3.11-slim-bullseye

# Install Tesseract OCR and Poppler in ONE step
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-ara \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY backend/ .

# Start command
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}

