FROM python:3.11-slim

# Environment settings
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py \
    FLASK_RUN_HOST=0.0.0.0

# Set working directory
WORKDIR /app

# Install system dependencies (optional but helpful)
RUN apt-get update && apt-get install -y build-essential gcc

# Copy static files first to leverage layer caching
COPY static/ ./static/

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy rest of the codebase
COPY . .

# Expose Flask port
EXPOSE 5000

# Run the app
CMD ["flask", "run"]
