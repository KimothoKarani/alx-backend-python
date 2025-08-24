# Use slim 3.12 (good for Django 5.x)
FROM python:3.12-slim

# Git + build tools + pkg-config + MySQL client headers
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      git \
      ca-certificates \
      build-essential \
      pkg-config \
      default-libmysqlclient-dev \
 && rm -rf /var/lib/apt/lists/*

# Optional, but nice defaults
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
