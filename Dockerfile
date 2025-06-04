FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable stdout buffering
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py \
    FLASK_RUN_HOST=0.0.0.0

# Set working directory
WORKDIR /app

# Copy static files first to leverage caching
COPY static/ ./static/

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of the codebase
COPY . .

# Expose Flask port
EXPOSE 5000

# Optional: default run command
CMD ["flask", "run"]