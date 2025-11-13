FROM python:3.9-slim
# Set timezone environment variable
ENV TZ=America/Los_Angeles
# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libssl-dev \
    gcc \
    tzdata \
    libpq-dev && \
    rm -rf /var/lib/apt/lists/*
# Set timezone
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
# Upgrade pip
RUN pip install --upgrade pip --no-cache-dir
# Set working directory
WORKDIR /app
# Copy requirements file first to leverage Docker caching
COPY requirements.txt /app/
# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
# Copy application code
COPY . /app/
# Expose application ports
EXPOSE 5566
# Command to run the application
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:5566", "wsgi:app"]