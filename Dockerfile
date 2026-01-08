FROM python:3.13-slim

# Cache bust: v2 - Force rebuild to install Tesseract OCR
ARG CACHEBUST=2

# Install system dependencies for OCR
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-ara \
    poppler-utils \
    libpoppler-cpp-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set Tesseract environment variable (Debian uses /usr/share/tesseract-ocr/4.00/tessdata)
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata

# Verify OCR installation - build will fail if these aren't installed
RUN tesseract --version && echo "✅ Tesseract installed successfully"
RUN which pdftoppm && echo "✅ Poppler installed successfully"
RUN ls -la /usr/share/tesseract-ocr/ && echo "✅ Tessdata directory found"

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

