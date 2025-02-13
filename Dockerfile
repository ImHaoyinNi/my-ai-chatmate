FROM python:3.12-slim

# Install build dependencies (GCC, PortAudio, Python headers, etc.)
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    libportaudio2 \
    portaudio19-dev \
    libsndfile1 \
    python3-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory to /app (so all paths are relative to this)
WORKDIR /app

# Copy the requirements-prod.txt file and install Python dependencies
COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . .

RUN sed -i '/^ENV=/d' .env && echo "\nENV=production" >> .env

# Set the command to run the app as a module
CMD ["python", "-m", "src.main"]

