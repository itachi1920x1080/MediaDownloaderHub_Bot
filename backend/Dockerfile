FROM python:3.13-slim

# Install ffmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Need psycopg2 for Neon/PostgreSQL support (or pymysql for MySQL)
RUN pip install --no-cache-dir psycopg2-binary

# Copy backend files
COPY . .

# Make start script executable
RUN chmod +x start.sh

# Start both bot and web API
CMD ["./start.sh"]
