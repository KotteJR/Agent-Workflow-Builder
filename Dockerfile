FROM python:3.13-bookworm

# Install system dependencies for OCR - MUST RUN FIRST
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-ara \
    poppler-utils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Verify Tesseract is installed - FAIL BUILD IF NOT
RUN which tesseract && tesseract --version
RUN which pdftoppm && pdftoppm -v

# Find tessdata location dynamically
RUN find /usr -name "tessdata" -type d 2>/dev/null || echo "tessdata not found"

# Set Tesseract environment variable
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend application code
COPY backend/ .

# Expose port (Railway sets PORT env variable)
EXPOSE 8000

# Run the application
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]

