# Use Python 3.9 slim image with explicit AMD64 platform
FROM --platform=linux/amd64 python:3.9-slim

# Set working directory
WORKDIR /app

# Create input and output directories
RUN mkdir -p /app/input /app/output

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the main Python files
COPY round1a_outline_extractor.py .
COPY run_round1a.py .

# Set the default command to run the processor
CMD ["python", "run_round1a.py", "/input", "/output"]