FROM python:3.11.7

# Install git if needed
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt ./

# Upgrade pip and install dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy rest of the repo
COPY . .

# Run bot as module (resolves imports correctly)
CMD ["python3", "-m", "Deendayal_botz.bot"]
