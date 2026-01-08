FROM python:3.13-slim

# Install system dependencies for OCR
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-ara \
    poppler-utils \
    libpoppler-cpp-dev \
    && rm -rf /var/lib/apt/lists/*

# Set Tesseract environment variable
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata

# Verify OCR installation
RUN tesseract --version && echo "Tesseract installed successfully"
RUN which pdftoppm && echo "Poppler installed successfully"

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

