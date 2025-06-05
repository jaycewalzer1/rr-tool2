FROM python:3.11-slim

# Prevent .pyc files and force stdout logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_RUN_HOST=0.0.0.0 \
    FLASK_APP=app:create_app

# Set working dir
WORKDIR /app

# Copy static files first for better cache
COPY static/ ./static/

# Install Python deps
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy app code
COPY . .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
