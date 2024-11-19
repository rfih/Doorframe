# Use the official Python image as the base image
FROM python:3.9-slim

# Install system dependencies required for tkinter
RUN apt-get update && apt-get install -y \
    python3-tk \
    && apt-get clean

RUN apt-get update && apt-get install -y \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container

WORKDIR /app

# Copy the application files to the container
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set the command to run your app
CMD ["xvfb-run", "python", "Appmajor.py"]
