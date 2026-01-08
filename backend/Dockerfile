FROM python:3.11-slim-bullseye

# Install Tesseract OCR and Poppler
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-ara \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install dependencies (context is backend/)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}

