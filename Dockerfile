FROM python:3.11-slim

# Prevent .pyc files and force stdout logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies including Tesseract
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    libleptonica-dev \
    poppler-utils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy static assets (for better caching)
COPY static/ ./static/

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy full app source
COPY . .

# Expose port
EXPOSE 5000

# Use Gunicorn in production
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
