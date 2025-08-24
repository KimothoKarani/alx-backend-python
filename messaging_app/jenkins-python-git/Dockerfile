# Start from official Python image
FROM python:3.9

# Install git (and clean up apt cache to keep image small)
RUN apt-get update && \
    apt-get install -y git && \
    rm -rf /var/lib/apt/lists/*
