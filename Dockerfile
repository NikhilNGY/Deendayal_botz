FROM python:3.11.7

RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

# Use a clean working directory
WORKDIR /app

# Copy everything into /app
COPY . .

# Upgrade pip and install requirements
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Run bot as module (resolves imports)
CMD ["python3", "-m", "Deendayal_botz.bot"]
